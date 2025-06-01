CREATE OR REPLACE TABLE mars_index_industry2 AS
WITH joined_factors AS ( -- spojujeme normalizované hodnoty faktorů
    SELECT 
        gw.latitude, 
        gw.longitude,
        gw.gw_norm, 
        s.stormy_days_normalized, 
        tt.cold_night_c_norm, 
        th_r.th_norm_r, 
        COALESCE(w.water_conc_norm, 0) AS water_conc_norm, 
        COALESCE(cl.cl_norm, 0) AS cl_norm, 
        COALESCE(fe.fe_norm, 0) AS fe_norm, 
        k.k_norm, 
        COALESCE(si.si_norm, 0) AS si_norm -- koncentrace křemíku
   FROM gw

   -- Používáme INNER JOIN u datasetů, o kterých víme, že obsahují všechny souřadnice, 
   -- a LEFT JOIN u datasetů, kde některé hodnoty mohou chybět
   
    INNER JOIN storms s 
        ON gw.latitude = s.latitude AND gw.longitude = s.longitude
    INNER JOIN temp_typ tt 
        ON gw.latitude = tt.latitude AND gw.longitude = tt.longitude
    LEFT JOIN th_conc_r th_r 
        ON gw.latitude = th_r.latitude AND gw.longitude = th_r.longitude
    LEFT JOIN w_conc w 
        ON gw.latitude = w.latitude AND gw.longitude = w.longitude
    LEFT JOIN cl_conc cl 
        ON gw.latitude = cl.latitude AND gw.longitude = cl.longitude
    LEFT JOIN fe_conc fe 
        ON gw.latitude = fe.latitude AND gw.longitude = fe.longitude
    LEFT JOIN k_conc k 
        ON gw.latitude = k.latitude AND gw.longitude = k.longitude
    LEFT JOIN si_conc si 
        ON gw.latitude = si.latitude AND gw.longitude = si.longitude
)
SELECT *, -- počítáme index pro průmysl
    (
        4*gw_norm + -- gravitační vlny
        4*stormy_days_normalized + -- počet bouřkových dnů 
        3*cold_night_c_norm + -- minimální teplota
        2*th_norm_r + -- koncentrace thoria
        8*water_conc_norm + -- koncentrace vody
        8*si_norm + -- koncentrace křemíku
        1*fe_norm + -- koncentrace železa
        1*cl_norm + -- koncentrace chloru
        1*k_norm -- koncentrace draslíku
    ) / (4+4+3+2+8+8+1+1+1) AS index_ind
FROM joined_factors;

