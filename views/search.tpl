%import re
%import os
<div class="container">
<div class="well">
<form action="results" method="get" class="form-horizontal">
<fieldset>
<legend>Search</legend>
<div class="form-group">
      <label for="inputEmail" class="col-lg-2 control-label">Query</label>
      <div class="col-lg-10">
        %if query['searchtype'] == 1:
            <input type="text" id="typeahead" class="form-control" name="query" placeholder="{{query['query'][1:-2]}}" value="{{query['query'][1:-2]}}">
        %end
        %if query['searchtype'] == 2:
            <input type="text" id="typeahead" class="form-control" name="query" placeholder="{{query['query'][6:-1]}}" value="{{query['query'][9:-1]}}">
        %end
        %if query['searchtype'] == 3:
            <input type="text" id="typeahead" class="form-control" name="query" placeholder="{{query['query']}}" value="{{query['query']}}">
        %end
        %if query['searchtype'] == 4:
            <input type="text" id="typeahead" class="form-control" name="query" placeholder="{{query['query'][1:-1]}}" value="{{query['query'][1:-1]}}">
        %end
	</div>
</div>
<div class="form-group">
      <label for="select" class="col-lg-2 control-label">Search Type</label>
      <div class="col-lg-10">
        <select name="searchtype" class="form-control" id="select">
        %if query['searchtype'] == 1:
                <option value="1" selected>Exact Phrase</option>
                <option value="2">Answer Line</option>
                <option value="3">All these words (manual mode)</option>
        %end
        %if query['searchtype'] == 2:
                <option value="1">Exact Phrase</option>
                <option value="2" selected>Answer Line</option>
                <option value="3">All these words (manual mode)</option>
        %end
        %if query['searchtype'] == 3:
                <option value="1">Exact Phrase</option>
                <option value="2">Answer Line</option>
                <option value="3" selected>All these words (manual mode)</option>
        %end
        </select><br>
      </div>
</div>
<div class="form-group">
      <label for="select" class="col-lg-2 control-label">Folder</label>
      <div class="col-lg-10">
        <select name="dir" id="folders" class="form-control">
        %for d in filter(None, sorted(dirs, key=lambda p: (p.count(os.path.sep), p))):
            %style = "margin-left: %dem" % (2*d.count('/'))
            %if d in query['dir']:
                <option style="{{style}}" selected value="{{d}}">{{re.sub('.+/','', d).replace("_", " ")}}</option>
            %else:
                <option style="{{style}}" value="{{d}}">{{re.sub('.+/','', d).replace("_", " ")}}</option>
            %end
        %end
        </select><br>
      </div>
</div>
<div id="collapseOne" class="accordion-body collapse">
<div class="form-group">
      <label for="select" class="col-lg-2 control-label">Sort by</label>
      <div class="col-lg-10">
        <select name="sort" class="form-control" id="select">
        %for s in sorts:
            %if query['sort'] == s[0]:
                <option selected value="{{s[0]}}">{{s[1]}}</option>
            %else:
                <option value="{{s[0]}}">{{s[1]}}</option>
            %end
        %end
        </select><br>
      </div>
</div>
<div class="form-group">
      <label for="select" class="col-lg-2 control-label">Order</label>
      <div class="col-lg-10">
        <select name="ascending" class="form-control" id="select">
            %if int(query['ascending']) == 1:
                <option value="0">Descending</option>
                <option value="1" selected>Ascending</option>
            %else:
                <option value="0" selected>Descending</option>
                <option value="1">Ascending</option>
            %end
        </select><br>
      </div>
</div>
</div>
<div class="form-group">
      <div class="col-lg-12 col-lg-offset-2">
	<a class="accordion-toggle btn btn-default" data-toggle="collapse" href="#collapseOne"> Options</a>
        <button type="submit" class="btn btn-primary">Search</button>
      </div>
</div>
<input type="hidden" name="page" value="1" />
</fieldset>
</form>
</div>
</div>
