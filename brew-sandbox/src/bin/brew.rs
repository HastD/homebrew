// SPDX-FileCopyrightText: Copyright 2026 Daniel Hast
//
// SPDX-License-Identifier: Apache-2.0 OR MIT

use std::{
    env,
    fs::{File, create_dir_all},
    io::{self, BufRead, BufReader, ErrorKind},
    os::unix::{fs::symlink, process::CommandExt},
    path::PathBuf,
    process::Command,
};

use anyhow::{Result, bail};
use landlock::{
    ABI, Access, AccessFs, AccessNet, NetPort, Ruleset, RulesetAttr, RulesetCreatedAttr,
    RulesetStatus, Scope, path_beneath_rules,
};
use tracing::{debug, level_filters::LevelFilter, warn};

const PORT_HTTPS: u16 = 443;

const SANDBOX_ENV_VAR: &str = "_HOMEBREW_SANDBOX";
const DEBUG_ENV_VAR: &str = "_HOMEBREW_SANDBOX_DEBUG";

const BREW_SYMLINK_PATH: &str = "/home/linuxbrew/.linuxbrew/.sandbox/brew-unsandboxed";
const BREW_TARGET_PATH: &str = "../Homebrew/bin/brew";

/// Create symlink to brew executable to replace the one that's overridden by
/// the sandbox executable. Fails if the symlink target doesn't exist.
fn make_brew_symlink() -> Result<()> {
    let brew_symlink_dir = PathBuf::from(BREW_SYMLINK_PATH.rsplit_once("/").unwrap().0);
    let brew_target_abspath = brew_symlink_dir.join(BREW_TARGET_PATH).canonicalize()?;
    if !brew_target_abspath.is_file() {
        bail!(
            "Brew executable not found at {}",
            brew_target_abspath.display()
        );
    }
    create_dir_all(brew_symlink_dir)?;
    match symlink(BREW_TARGET_PATH, BREW_SYMLINK_PATH) {
        Ok(()) => Ok(()),
        Err(err) if matches!(err.kind(), ErrorKind::AlreadyExists) => Ok(()),
        Err(err) => Err(err.into()),
    }
}

/// Apply Landlock sandbox to current thread, restricting filesystem, network,
/// and IPC access.
fn restrict_self() -> Result<()> {
    let abi = ABI::V6;
    let access_all = AccessFs::from_all(abi);
    let access_read = AccessFs::from_read(abi);
    let status = Ruleset::default()
        .handle_access(access_all)?
        .handle_access(AccessNet::from_all(abi))?
        .scope(Scope::from_all(abi))?
        .create()?
        .add_rules(path_beneath_rules(
            &["/etc", "/proc/cpuinfo", "/usr"],
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
                "/home/linuxbrew",
                "/var/tmp/homebrew",
            ],
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
    if !status.no_new_privs {
        warn!("Failed to restrict privileges (PR_SET_NO_NEW_PRIVS not set).")
    }
    Ok(())
}

/// Read environment and config files to determine whether sandboxing should be applied.
fn should_sandbox() -> Result<bool> {
    let env_var_test =
        |value: &str| !value.is_empty() && value != "0" && value.to_lowercase() != "false";

    if let Ok(sandbox_var) = env::var(SANDBOX_ENV_VAR) {
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

/// Initialize tracing subscriber that prints to stderr at the selected log level.
fn init_logging() {
    let filter = if env::var_os(DEBUG_ENV_VAR).is_some() {
        LevelFilter::DEBUG
    } else {
        LevelFilter::WARN
    };
    tracing_subscriber::fmt()
        .compact()
        .with_max_level(filter)
        .without_time()
        .with_writer(io::stderr)
        .init();
}

fn main() -> Result<()> {
    // SAFETY: The program is single-threaded.
    unsafe {
        env::set_var("HOME", "/home/linuxbrew");
        env::set_var("XDG_CACHE_HOME", "/home/linuxbrew/.cache");
    }
    init_logging();
    if should_sandbox()? {
        restrict_self()?;
    } else {
        debug!("Not applying Landlock sandboxing due to {SANDBOX_ENV_VAR} setting.")
    }
    make_brew_symlink()?;
    let mut args = env::args_os();
    let error = Command::new(BREW_SYMLINK_PATH)
        .arg0(args.next().unwrap())
        .args(args)
        .exec();
    Err(error.into())
}
