%include header title=": " + query['query']+" ("+str(nres)+")"
%include navbar
%include search query=query, dirs=dirs, sorts=sorts
<div class="container">
<div class="panel panel-default">
<div class="panel-body">
    <div id="found">
        Found <span class="badge">{{nres}}</span> matching: <b><i>{{qs}}</i></b>
        in <span class="badge">({{time.seconds}}.{{time.microseconds/10000}}s)</span>
    </div>
    %if len(res) > 0:
        <div class="btn-group pull-right">
            <a class="btn btn-primary btn-xs" href="./json?{{query_string}}">JSON</a>
            <a class="btn btn-primary btn-xs" href="./csv?{{query_string}}">CSV</a>
        </div>
    %end
    <br style="clear: both">
</div>
</div>
</div>
%include pages query=query, config=config, nres=nres
<div id="results">
%for i in range(0, len(res)):
    %include result d=res[i], i=i, query=query, config=config,
%end
</div>
%include pages query=query, config=config, nres=nres
%include footer
<!-- vim: fdm=marker:tw=80:ts=4:sw=4:sts=4:et:ai
-->
