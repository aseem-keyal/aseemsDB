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
    <h4 id="r{{d['sha']}}" title="{{d['abstract']}}"><span class="badge"><a href="#r{{d['sha']}}">#{{number}}</a></span><a href="{{ ''.join(['http://aseemsdb.me', url[url.find('/static'):]]) }}"> {{d['label'].replace("_", " ")}}</a></h4>
    %if len(d['ipath']) > 0:
        <h5 class="search-result-ipath">[{{d['ipath']}}]</h5>
    %end
    %if  len(d['author']) > 0:
        <h5 class="search-result-author">by {{d['author']}}</h5>
    %end
    <h5 class="search-result-url">
    <!--
    If it has these words it's probably a bonus, the other words then its a TU
    -->
    % bonuses = ["for 10 points each", "for ten points each", "ftpe"]
    % tossups = ["for 10 points", "for ten points", "ftp"]
    <!--
    If we have an ellipsis then we find the portion of the text relevant by splitting
    by the ellipsis and finding the chunk with the query
    -->
    %if "..." in d['snippet'][:-4]:
        %for q in shlex.split(query['query'].replace("'","\\'")):
            % w = strip_accents(q.decode('utf-8').lower()).encode('utf-8')
            % w = w.replace("answer: ", "")
            % w = w.replace("\\", "")
            % w = w.replace("\'", " ")
            % w = w.replace(".", "")
        %end
        %snippets = d['snippet'].split("...")
        %for snipp in snippets:
            %if w in snipp:
                %snippet = snipp
            %end
        %end
    %else:
        %snippet = d['snippet']
    %end

    % try:
        % snippet
    % except NameError:
        % snippet = d['snippet']
    % else:
        % snippet = d['snippet']
    <!--
    Check if there are any bonus keywords, check if there are TU keywords, check
    if there are " 10 " which mean "[10]", otherwise it's probably a TU
    -->
    %if any(conv in snippet for conv in bonuses):
        <span class="badge">Bonus</span>
    %elif any(conv in snippet for conv in tossups):
        <span class="badge">Tossup</span>
    %elif snippet.count(" 10 ") > 0:
        <span class="badge">Bonus</span>
    %else:
        <span class="badge">Tossup</span>
    %end

        %urllabel = d['url'].replace('/'+d['filename'],'').replace('file://','')
        %for r in config['dirs']:
            %urllabel = urllabel.replace(r.rsplit('/',1)[0] + '/' , '')
        %end
        {{urllabel.replace("_", " ")}}
    </h5>
    <!--
    Highlight the search query by removing extraneous things from the query
    --!>
    %for q in shlex.split(query['query'].replace("'","\\'")):
        %if not q == "OR":
            % w = strip_accents(q.decode('utf-8').lower()).encode('utf-8')
            % w = w.replace("answer: ", "")
            % w = w.replace("\\", "")
            % w = w.replace("\'", " ")
            % w = w.replace(".", "")
            % d['snippet'] = d['snippet'].replace(w,'<mark>'+w+'</mark>')
        %end
    %end
    <blockquote>{{!d['snippet']}}</blockquote>
</div>
</div>
