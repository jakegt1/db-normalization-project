CREATE TABLE winners(
  tournament CHAR(50) NOT NULL,
  year integer NOT NULL,
  winner CHAR(50) NOT NULL,
  winnerdob date NOT NULL,
  courttype CHAR(50) NOT NULL,
  PRIMARY KEY ( year, tournament )
);

