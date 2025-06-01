CREATE OR REPLACE TABLE mars_index AS
WITH joined_factors AS ( -- spojujeme normalizované hodnoty faktorů
    SELECT 
        gw.latitude, 
        gw.longitude,
        gw.gw_norm,
        s.stormy_days_normalized,
        ta.annual_avg_c_norm,
        ta.annual_range_c_norm,
        tt.cold_night_c_norm,
        th.thconc_norm,
        COALESCE(w.water_conc_norm, 0) AS water_conc_norm
    FROM gw
    
    -- Používáme INNER JOIN u datasetů, o kterých víme, že obsahují všechny souřadnice, 
    -- a LEFT JOIN u datasetů, kde některé hodnoty mohou chybět

    JOIN storms s 
        ON gw.latitude = s.latitude AND gw.longitude = s.longitude
    JOIN temp_avg ta 
        ON gw.latitude = ta.latitude AND gw.longitude = ta.longitude
    JOIN temp_typ tt 
        ON gw.latitude = tt.latitude AND gw.longitude = tt.longitude
    LEFT JOIN th_conc th 
        ON gw.latitude = th.latitude AND gw.longitude = th.longitude
    LEFT JOIN w_conc w 
        ON gw.latitude = w.latitude AND gw.longitude = w.longitude
)
SELECT *, -- počítáme index obyvatelnosti
    (
        4*gw_norm + -- gravitační vlny
        4*stormy_days_normalized + -- počet bouřkových dnů
        1*annual_avg_c_norm + -- průměrná roční teplota
        3*annual_range_c_norm + -- roční teplotní rozsah
        2*cold_night_c_norm + -- minimální teplota
        2*thconc_norm + -- koncentrace thoria
        8*water_conc_norm -- koncentrace vody
    ) / (4+4+1+3+2+2+8) AS index_hab
FROM joined_factors;


