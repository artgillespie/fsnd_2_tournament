#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute('DELETE FROM match')
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute('DELETE FROM player')
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM player')
    count = cur.fetchone()
    conn.close()
    return count[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute('INSERT INTO player (name) VALUES (%s)', (name,))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    sql = """SELECT player.id, player.name, wins.count, COUNT(match.winner_id)
                 FROM player
                 LEFT JOIN match
                 ON match.loser_id=player.id
                 OR match.winner_id=player.id
                 LEFT JOIN wins
                 ON wins.id=player.id
                 GROUP BY player.id, player.name, wins.count
                 ORDER BY wins.count DESC
                 """
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    r = cur.fetchall()
    conn.close()
    return r


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    sql = """INSERT INTO match (loser_id, winner_id)
             VALUES (%s, %s)"""
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (loser, winner))
    conn.commit()


def previousMatch(a, b):
    """Checks to see if these two players have already had a match.

    Args:
        a: the id number of the first player to check.
        b: the id number of the second player to check.
    """
    sql = """SELECT COUNT(*) FROM match
             WHERE (loser_id = %s AND winner_id = %s)
             OR (loser_id = %s AND winner_id = %s)"""
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (a, b, b, a))
    r = cur.fetchone()[0]
    conn.close()
    return 1 == r


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # since playerStandings() comes back sorted by wins, we can just pair
    # neighbors in this list
    # TODO: ensure players haven't already played each other
    standings = playerStandings()
    ret = []
    for i in range(0, len(standings), 2):
        ret.append((standings[i][0], standings[i][1],
                    standings[i+1][0], standings[i+1][1]))

    return ret
