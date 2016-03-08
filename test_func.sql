CREATE TABLE winners_tournament(
  tournament CHAR(50) NOT NULL,
  courttype CHAR(50) NOT NULL,
  PRIMARY KEY ( tournament )
);

CREATE TABLE winners_winner(
  winner CHAR(50) NOT NULL,
  winnerdob date NOT NULL,
  PRIMARY KEY ( winner )
);

CREATE TABLE winners(
  tournament CHAR(50) NOT NULL,
  year integer NOT NULL,
  winner CHAR(50) NOT NULL,
  FOREIGN KEY ( winner ) REFERENCES winners_winner( winner ),
  FOREIGN KEY ( tournament ) REFERENCES winners_tournament( tournament ),
  PRIMARY KEY ( year, tournament )
);

