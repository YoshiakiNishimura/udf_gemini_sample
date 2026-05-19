DROP TABLE IF EXISTS t;
CREATE TABLE t (
  string_value VARCHAR(255)
);

INSERT INTO t VALUES (
 'タイの首都は？'
);

select ask_gemini(string_value) from t;
select ask_gemini_with_blob(blob1)  from b;
