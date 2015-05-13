select
adv_id,appdomain,adxname,pubid,decilecutoff,
COUNT(request_id) as I,
SUM(isclick) as C,
SUM(issale) as S,
AVG(cost_inr_cpm) as imprcost
from
BICS_tab 
where dt > 20150505
group by adv_id,appdomain,adxname,pubid,decilecutoff;

select
adv_id,appdomain,adxname,pubid,decilecutoff,
SUM(iswon) as wins,
AVG(bidvalue_cpm) as bidvalue,
AVG(ruleenginebid_inr_cpm) as enginebidvalue,
AVG(basebidvalue) as basebidvalue
from BICS_tab
where dt > 20150505
group by adv_id,appdomain,adxname,pubid,decilecutoff;

