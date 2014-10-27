%q = dict(query)
%if q['searchtype'] == 1:
    %q['query'] = q['query'][1:-1]
%end
%if q['searchtype'] == 2:
    %q['query'] = q['query'][9:-1]
%end
%def page_href(page):
	%q['page'] = page
	%return './results?%s' % urllib.urlencode(q)
%end
%if nres > 0:
	%import math, urllib
	%npages = int(math.ceil(nres/float(config['perpage'])))
	%if npages > 1:
		<div class="text-center">
		<div class="container">
		<ul class="pagination">
		<li><a title="First" class="page" href="{{page_href(1)}}">&#171;</a></li>
		<li><a title="Previous" class="page" href="{{page_href(max(1,query['page']-1))}}">&#8249;</a></li> &nbsp;
		%offset = ((query['page'])/10)*10
		%for p in range(max(1,offset), min(offset+10,npages+1)):
			%if p == query['page']:
				<li class="active">
			%else:
				<li>
			%end
			<a href="{{page_href(p)}}" class="page">{{p}}</a></li>
		%end
		&nbsp; <li><a title="Next" class="page" href="{{page_href(min(npages, query['page']+1))}}">&#8250;</a></li>
		<li><a title="Last" class="page" href="{{page_href(npages)}}">&#187;</a></li>
		</ul>
		</div>
		</div>
	%end
%end
