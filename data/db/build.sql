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
    dmUserOnModerationAction bool DEFAULT FALSE,
    deleteAllLinks bool DEFAULT TRUE,
    deleteBlacklistedLinks DEFAULT FALSE,
    deleteBlacklistedWords DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS guildSettings(
    GuildID integer PRIMARY KEY,
    modRole text,
    restrictedRole text,
    logChannel integer,
    welcomeChannel integer,
    suggestionChannel integer,
    suggestModule DEFAULT TRUE,
    moderationModule DEFAULT TRUE,
    welcomeModule DEFAULT TRUE,
    coinEmoji text,
    lotteryPrice integer DEFAULT 5
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

CREATE TABLE IF NOT EXISTS suggestions(
    rowNumber integer PRIMARY KEY,
    suggestNumber integer,
    GuildID integer,
    SubmitterID integer,
    suggestion text,
    status text
);

CREATE TABLE IF NOT EXISTS economy(
    GuildID integer,
    UserID integer,
    balance integer DEFAULT 0,
    maxCoinsInCirculation integer DEFAULT 1000000
);

CREATE TABLE IF NOT EXISTS shop(
    GuildID integer PRIMARY KEY,
    item1 text,
    item2 text,
    item3 text,
    item4 text,
    item5 text,
    item6 text
);

