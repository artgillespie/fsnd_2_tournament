-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP TABLE IF EXISTS player CASCADE;
CREATE TABLE player (
	id serial PRIMARY KEY,
	name text 
);

DROP TABLE IF EXISTS match CASCADE;
CREATE TABLE match (
	loser_id int references player (id),
	winner_id int references player (id)
);

DROP VIEW IF EXISTS wins CASCADE;
CREATE VIEW wins AS SELECT player.id AS id, COUNT(match.winner_id) AS count
    FROM player
    LEFT JOIN match
    ON player.id=match.winner_id
    GROUP BY player.id;

	
	


