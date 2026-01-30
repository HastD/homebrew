// SPDX-FileCopyrightText: Copyright 2026 Daniel Hast
//
// SPDX-License-Identifier: Apache-2.0 OR MIT

use std::{
    fs::{File, create_dir_all},
    io::{BufRead, BufReader, ErrorKind},
    os::unix::{fs::symlink, process::CommandExt},
    path::PathBuf,
    process::Command,
    sync::LazyLock,
};

use anyhow::Result;
use landlock::{
    ABI, Access, AccessFs, AccessNet, NetPort, Ruleset, RulesetAttr, RulesetCreatedAttr,
    RulesetStatus, path_beneath_rules,
};
use tracing::{debug, level_filters::LevelFilter, warn};

const PORT_HTTPS: u16 = 443;

const SANDBOX_ENV_VAR: &str = "_HOMEBREW_SANDBOX";
const DEBUG_ENV_VAR: &str = "_HOMEBREW_SANDBOX_DEBUG";

static HOMEBREW_PREFIX: LazyLock<PathBuf> = LazyLock::new(|| {
    std::env::var_os("HOMEBREW_PREFIX")
        .unwrap_or_else(|| "/home/linuxbrew/.linuxbrew".into())
        .into()
});

static HOMEBREW_CACHE: LazyLock<PathBuf> = LazyLock::new(|| {
    std::env::var_os("HOMEBREW_CACHE")
        .unwrap_or_else(|| "/home/linuxbrew/.cache/Homebrew".into())
        .into()
});

fn brew_path() -> PathBuf {
    HOMEBREW_PREFIX.join(".sandbox/brew-unsandboxed")
}

fn make_brew_symlink() -> Result<()> {
    create_dir_all(HOMEBREW_PREFIX.join(".sandbox"))?;
    match symlink("../Homebrew/bin/brew", brew_path()) {
        Ok(()) => Ok(()),
        Err(err) if matches!(err.kind(), ErrorKind::AlreadyExists) => Ok(()),
        Err(err) => Err(err.into()),
    }
}

fn restrict_self() -> Result<()> {
    let abi = ABI::V6;
    let access_all = AccessFs::from_all(abi);
    let access_read = AccessFs::from_read(abi);
    let status = Ruleset::default()
        .handle_access(access_all)?
        .handle_access(AccessNet::from_all(abi))?
        .create()?
        .add_rules(path_beneath_rules(
            &["/etc", "/home/linuxbrew", "/proc/cpuinfo", "/usr"],
            access_read,
        ))?
        .add_rules(path_beneath_rules(
            &[
                "/dev/null",
                "/dev/ptmx",
                "/dev/pts",
                "/dev/random",
                "/dev/urandom",
                "/dev/zero",
                "/var/tmp/homebrew",
            ],
            access_all,
        ))?
        .add_rules(path_beneath_rules(
            &[&**HOMEBREW_CACHE, &**HOMEBREW_PREFIX],
            access_all,
        ))?
        .add_rule(NetPort::new(PORT_HTTPS, AccessNet::ConnectTcp))?
        .restrict_self()?;
    match status.ruleset {
        RulesetStatus::FullyEnforced => debug!("Landlock sandboxing fully enforced."),
        RulesetStatus::PartiallyEnforced => {
            warn!("Landlock sandboxing only partially enforced.")
        }
        RulesetStatus::NotEnforced => warn!("Landlock sandboxing not enforced."),
    }
    Ok(())
}

fn should_sandbox() -> Result<bool> {
    let env_var_test =
        |value: &str| !value.is_empty() && value != "0" && value.to_lowercase() != "false";

    if let Ok(sandbox_var) = std::env::var(SANDBOX_ENV_VAR) {
        return Ok(env_var_test(&sandbox_var));
    }

    if let Ok(file) = File::open("/etc/homebrew/brew-sandbox.env") {
        for line in BufReader::new(file).lines() {
            if let Some((key, value)) = line?.split_once("=")
                && key.trim() == SANDBOX_ENV_VAR
            {
                let value = value.trim();
                return Ok(env_var_test(value));
            }
        }
    }

    Ok(true)
}

fn init_logging() {
    let filter = if std::env::var_os(DEBUG_ENV_VAR).is_some() {
        LevelFilter::DEBUG
    } else {
        LevelFilter::WARN
    };
    tracing_subscriber::fmt()
        .compact()
        .with_max_level(filter)
        .without_time()
        .with_writer(std::io::stderr)
        .init();
}

fn main() -> Result<()> {
    // SAFETY: The program is single-threaded.
    unsafe {
        std::env::set_var("HOME", "/home/linuxbrew");
        std::env::set_var("XDG_CACHE_HOME", "/home/linuxbrew/.cache");
    }
    init_logging();
    if should_sandbox()? {
        restrict_self()?;
    } else {
        debug!("Not applying Landlock sandboxing due to {SANDBOX_ENV_VAR} setting.")
    }
    make_brew_symlink()?;
    let mut args = std::env::args_os();
    let error = Command::new(brew_path())
        .arg0(args.next().unwrap())
        .args(args)
        .exec();
    Err(error.into())
}
