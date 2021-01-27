DROP TABLE IF EXISTS public.metric_status;
DROP TABLE IF EXISTS public.metric_latency;
DROP TABLE IF EXISTS public.metric_content_matcher;
DROP TABLE IF EXISTS public.website;


create table if not exists public.website
(
	id serial constraint website_pk primary key,
	url varchar not null,
	created_at timestamp not null default CURRENT_TIMESTAMP
);

create unique index if not exists website_url_uindex on public.website (url);


create table if not exists public.metric_status
(
	id serial constraint metric_status_pk primary key,
	website_id integer not null,
	record_id varchar not null,
	httpstatus int not null,
	httpmessage varchar,
	collected_at varchar,
	created_at timestamp not null default current_timestamp,
	constraint fk_website_metric_status foreign key(website_id) references public.website(id)
);

create unique index if not exists metric_status_record_id_uindex on public.metric_status (record_id);


create table if not exists public.metric_latency
(
	id serial constraint metric_latency_pk primary key,
	website_id integer not null,
	record_id varchar not null,
	latency real not null,
	collected_at varchar,
	created_at timestamp not null default current_timestamp,
	constraint fk_website_metric_latency foreign key(website_id) references public.website(id)
);

create unique index if not exists metric_latency_record_id_uindex on public.metric_latency (record_id);

create table if not exists public.metric_content_matcher
(
	id serial constraint metric_content_matcher_pk primary key,
	website_id integer not null,
	record_id varchar not null,
	content_pattern varchar,
	result bool not null,
	collected_at varchar,
	created_at timestamp not null default current_timestamp,
	constraint fk_website_metric_content_matcher foreign key(website_id) references public.website(id)
);

create unique index if not exists metric_content_matcher_id_uindex on public.metric_content_matcher (record_id);
