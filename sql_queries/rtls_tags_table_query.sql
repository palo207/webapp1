create table rtls_tags (row_no integer Identity(1,1) primary key,
tag_id varchar(50),
address varchar(50),
PosX float,
PosY float,
zone_id varchar(50),
zone_type varchar(50),
zone_name varchar(50),
zone_entered datetime not null default current_timestamp,
paired bit,
paired_id varchar(50)
)