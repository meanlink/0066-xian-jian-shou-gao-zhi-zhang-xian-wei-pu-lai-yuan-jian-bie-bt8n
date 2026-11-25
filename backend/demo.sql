INSERT INTO paper_cases VALUES ('MS41','D3-11','汊口航程簿','imaged','2026-11-24'),
 ('MS42','B5-03','小碑校录散页','intake','2026-11-24'),('MS46','D3-12','岸边诗稿','imaged','2026-11-24') ON CONFLICT DO NOTHING;
INSERT INTO paper_impressions VALUES ('MS41',1,7,83,11,30,'MS41-a.tif'),('MS46',1,45,49,12,30,'MS46-a.tif') ON CONFLICT DO NOTHING;
INSERT INTO paper_references VALUES
 ('C01','C-A','旧棉布纸',83,10,12,24,true),('C02','C-B','旧棉布纸',88,14,9,32,true),('C03','C-C','旧棉布纸',85,11,8,50,true),
 ('R01','R-A','苇浆纸',11,83,9,26,true),('R02','R-B','苇浆纸',10,88,11,30,true),('R03','R-C','苇浆纸',8,87,15,48,true),
 ('B01','B-A','韧皮纤维纸',12,10,88,30,true),('B02','B-B','韧皮纤维纸',11,9,82,32,true),('B03','B-C','韧皮纤维纸',14,10,85,30,true),
 ('Q01','Q-X','旧棉布纸',41,42,43,8,false) ON CONFLICT DO NOTHING;
