%import shlex, unicodedata
%import string
%def strip_accents(s): return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
<div class="container">
<div class="well well-sm">
    %number = (query['page'] - 1)*config['perpage'] + i + 1

    %url = d['url'].replace('file://', '')
    %for dr, prefix in config['mounts'].items():
        %url = url.replace(dr, prefix)
    %end
    <h4 id="r{{d['sha']}}" title="{{d['abstract']}}"><span class="badge"><a href="#r{{d['sha']}}">#{{number}}</a></span><a href="{{ ''.join(['http://localhost:8080', url[url.find('/static'):]]) }}"> {{d['label']}}</a></h4>
    %if len(d['ipath']) > 0:
        <h5 class="search-result-ipath">[{{d['ipath']}}]</h5>
    %end
    %if  len(d['author']) > 0:
        <h5 class="search-result-author">by {{d['author']}}</h5>
    %end
    <h5 class="search-result-url">
        %urllabel = d['url'].replace('/'+d['filename'],'').replace('file://','')
        %for r in config['dirs']:
            %urllabel = urllabel.replace(r.rsplit('/',1)[0] + '/' , '')
        %end
        {{urllabel}}
    </h5>
    %for q in shlex.split(query['query'].replace("'","\\'")):
        %if not q == "OR":
            % w = strip_accents(q.decode('utf-8').lower()).encode('utf-8')
            % w = w.replace("answer: ", "")
            % w = w.translate(string.maketrans("",""), string.punctuation)
            % d['snippet'] = d['snippet'].replace(w,'<mark>'+w+'</mark>')
        %end
    %end
    <blockquote>{{!d['snippet']}}</blockquote>
</div>
</div>
