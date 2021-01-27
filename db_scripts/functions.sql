/* ******************************************************************
 	File	:  functions.sql
	Date	: 25 Jan 2021
	Author: Florentio

******************************************************************* */

create or replace function public.add_metric_data(payload jsonb)
 returns text
 language plpgsql
 security definer
as $function$

declare
  _website_id bigint = 0;
  _metric_status_id bigint = 0;
  _metric_latency_id bigint = 0;
  _metric_content_matcher_id bigint = 0;
  _website public.website%rowtype;
  _metric_status public.metric_status%rowtype;
  _metric_latency public.metric_latency%rowtype;
  _metric_content_matcher public.metric_content_matcher%rowtype;

begin
    raise info '__Running add_metric_data';

    select * from public.website where website.url = payload->>'url' into _website;

    if found then
        raise info 'website already exists';
        _website_id = _website.id;
    else
        raise info 'insert new website';
        insert into public.website(url) values (payload->>'url') returning id into _website_id;
    end if;

    select * from public.metric_status where metric_status.record_id = payload->>'message_id' into _metric_status;

    if found then
        raise info 'metric_status already exists';
        _metric_status_id = _metric_status.id;
    else
        raise info 'insert new metric_status';
        insert into public.metric_status(website_id, record_id, httpstatus, httpmessage, collected_at)
        values (_website_id, payload->>'message_id', (payload->>'status')::int, payload->>'desc', payload->>'at') returning id into _metric_status_id;
    end if;

    select * from public.metric_latency where metric_latency.record_id = payload->>'message_id' into _metric_latency;

    if found then
        raise info 'metric_latency already exists';
        _metric_latency_id = _metric_latency.id;
    else
        raise info 'insert new metric_latency';
        insert into public.metric_latency(website_id, record_id, latency, collected_at)
        values (_website_id, payload->>'message_id', (payload->>'latency')::real, payload->>'at') returning id into _metric_latency_id;
    end if;

     select * from public.metric_content_matcher where metric_content_matcher.record_id = payload->>'message_id' into _metric_content_matcher;

    if found then
        raise info 'metric_content_matcher already exists';
        _metric_content_matcher_id = _metric_content_matcher.id;
    else
        raise info 'insert new metric_content_matcher';
        insert into public.metric_content_matcher(website_id, record_id, content_pattern, result, collected_at)
        values (_website_id, payload->>'message_id', coalesce(payload->>'content_pattern', ''), (payload->>'page_content_ok')::bool , payload->>'at') returning id into _metric_content_matcher_id;
    end if;
    return (payload->>'message_id')::text;
end;
$function$;
