CREATE TABLE IF NOT EXISTS guilds(
    GuildID integer PRIMARY KEY,
    Prefix text DEFAULT ".",
    logMessages bool DEFAULT TRUE,
    logGuildChanges bool DEFAULT TRUE,
    logUserUpdates bool DEFAULT TRUE,
    logMemberLeave bool DEFAULT TRUE,
    logModerationActions bool DEFAULT TRUE,
    dmUserOnKickOrBan bool DEFAULT FALSE,
    logActionsDoneByBots bool DEFAULT FALSE,
    dmUserOnModerationAction bool DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS guildSettings(
    GuildID integer PRIMARY KEY,
    modRole text,
    restrictedRole text,
    logChannel integer
);

CREATE TABLE IF NOT EXISTS exp (
	UserID integer PRIMARY KEY,
	Username text,
	XP integer DEFAULT 0,
	Level integer DEFAULT 0,
	XPLock text DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS restricted(
    UserID integer PRIMARY KEY,
    durationTillUnrestricted integer
);


