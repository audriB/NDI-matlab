% a) Ready for review (function setLabel): Add a function to show where this gui is opened
% b) Ready for review (function closeGUI): Add a method to close the GUI (and clear table, and remove docs in this method)
% c) Ready for review (function removeDocs): Add a removeDocs method
% d) Ready for review: Add help for all method

classdef docViewer < handle
    
    properties
        fullDocuments = []; % docs
        fullTable = {}; % store whole file list
        tempDocuments = []; % temp doc on the right        
        tempTable = {}; % temp list on the left
        search; % search textbox
        table; % left table
        panel; % right panel
        info; % data for function details
        docs; % original docs file (file as a variable stored in mat format)
        source = 'New Doc Viewer'; % where is this gui opened, defualt = 'New Doc Viewer'
	fig; % figure handle
    end
    
    methods
        function obj = docViewer(source)
        % Initializes a new doc viewer GUI
            if exist('source','var')
                obj.source = source; % set source to where it is opened
            end

            obj.fig = figure('name','Document Viewer','NumberTitle','off');
        
            obj.setLabel(obj.source);
        
            obj.table = uitable('units', 'normalized', 'Position', [2/36 2/24 20/36 18/24], ...
                                'ColumnName', {'Name'; 'ID'; 'Type'; 'Date'}, ...
                                'ColumnWidth', {100, 100, 100, 100}, ...
                                'Data', {}, 'CellSelectionCallback', @obj.details);
                            
            obj.panel = uipanel('Position', [20/36 2/24 14/36 20/24], 'BackgroundColor', 'white');
            
            obj.search = [uicontrol('units', 'normalized', 'Style', 'popupmenu', 'FontSize', 10.25, ...
                                    'Position', [2/36 20/24 5/36 2/24], 'String', {'Select' 'Name' 'ID' 'Type' 'Date' 'Other'}, ...
                                    'BackgroundColor', [0.9 0.9 0.9]) ...
                          uicontrol('units', 'normalized', 'Style', 'popupmenu', 'FontSize', 10.25, ...
                                    'Position', [2/36 19/24 5/36 2/24], 'String', {'Filter options' 'contains' 'begins with' 'ends with'}, ...
                                    'BackgroundColor', [0.9 0.9 0.9]) ...
                          uicontrol('units', 'normalized', 'Style', 'edit', ...
                                    'Position', [7/36 20/24 5/36 2/24], 'String', '', ...
                                    'BackgroundColor', [1 1 1]) ...
                          uicontrol('units', 'normalized', 'Style', 'pushbutton', ...
                                    'Position', [12/36 20/24 4/36 1/24], 'String', 'Search field name', ...
                                    'BackgroundColor', [0.9 0.9 0.9], 'Callback', @obj.searchFieldName) ...
                          uicontrol('units', 'normalized', 'Style', 'pushbutton', ...
                                    'Position', [12/36 21/24 4/36 1/24], 'String', 'Search by filter', ...
                                    'BackgroundColor', [0.9 0.9 0.9], 'Callback', @obj.filter) ...
                          uicontrol('units', 'normalized', 'Style', 'pushbutton', ...
                                    'Position', [16/36 20/24 4/36 1/24], 'String', 'Clear table', ...
                                    'BackgroundColor', [0.9 0.9 0.9], 'Callback', @obj.clearView)...
                          uicontrol('units', 'normalized', 'Style', 'pushbutton', ...
                                    'Position', [16/36 21/24 4/36 1/24], 'String', 'Restore', ...
                                    'BackgroundColor', [0.9 0.9 0.9], 'Callback', @obj.restore)...
                          uicontrol('units', 'normalized', 'Style', 'pushbutton', ...
                                    'Position', [16/36 22/24 4/36 1/24], 'String', 'Remove docs', ...
                                    'BackgroundColor', [0.9 0.9 0.9], 'Callback', @obj.removeDocs)];
        end
        
        function closeGUI(obj)
        % Close current doc viewer GUI
        % Input: obj
        % Usage:
        %   (First you should create a gui like this: newDocViewer = docViewer();)
        %   newDocViewer.closeGUI(); % Should close this current gui newDocViewer 
            obj.fullTable = {}; % Clear table
            obj.table.Data = {}; % Remove data
            close(obj.fig); % Close GUI
        end
        
        function setLabel(~, source)
        % Set obj.source so that the user knows where this gui is opened
        % Usage: 
        %   newDocViewer = docViewer();
        %   newDocViewer.setLabel('New Label')
            uicontrol('units', 'normalized','Style','text','String',source,'FontSize',11,'Position',[2/36 22/24 12/36 2/24]);
        end
        
        function addDoc(obj,docs)
		% Load a list of docs from a mat file, each doc should be stored as
		% a cell in a cell array
        % 
        % Input: docs, a cell array
        % Usage: 
        %    newDocViewer = docViewer();
        %    docs = load('SomeDocuments.mat');
        %    newDocViewer.addDoc(docs.documents);

            for i=1:numel(docs)
                d = docs{i}.document_properties.ndi_document;
                obj.fullTable(end+1,:) = {d.name d.id d.type d.datestamp};
            end
            obj.fullDocuments = transpose([docs{:}]);
            obj.tempTable = obj.fullTable;
            obj.tempDocuments = obj.fullDocuments;
            obj.table.Data = obj.fullTable;
            obj.docs = docs;
        end

        function removeDocs(obj, ~, ~)
        % Remove loaded docs from current docViewer, this will clear the view AND remove the docs 
        % (method clear will only clear the view)
        % If the user clears table, they can use the restore button to restore the table,
        % but if the user removes docs, they cannot restore table
        
            removeAns = questdlg({'Are you sure you want to remove all documents? ',
                                'This will remove all documents from docViewer and you need to reload to see them again.',
                                'If you want to keep the documents while clearing the view, please use the Clear table button.'}, ...
                                'Remove all documents', ...
                                'No, go back', 'Yes, remove all', 'Yes, remove all');
            if strcmp(removeAns,'Yes, remove all')
                obj.fullTable = {};
                obj.table.Data = {};
            end
        end
        
        function details(obj, ~, event)
        % Displays the detail of a document when the user clicks on the cell
        
            if ~isempty(event.Indices)
                id = obj.table.Data(event.Indices(1),:);
                % add jsonDetails to id
                jsonDetails = obj.fullDocuments([event.Indices(1)]).document_properties;
                jsonDetails = jsonencode(jsonDetails, "PrettyPrint", true);
                id{end+1} = jsonDetails;
                delete(obj.info);
                obj.info = [uicontrol(obj.panel, 'units', 'normalized', 'Style', 'text', ...
                                      'Position', [0 15/16 1 1/16], 'String', 'Name:', ...
                                      'BackgroundColor', [1 1 1], 'FontWeight', 'bold') ...
                            uicontrol(obj.panel, 'units', 'normalized', 'Style', 'text', ...
                                      'Position', [0 14/16 1 1/16], 'String', id{1}, ...
                                      'BackgroundColor', [1 1 1]) ...
                            uicontrol(obj.panel, 'units', 'normalized', 'Style', 'List', ...
                                      'Position', [0 1/4 1 10/16], 'min', 0, 'max', 2, ...
                                      'String', {'Type:' id{3} '' 'Date:' id{4} '' 'ID:' id{2} '' 'Content:' id{5}}, ...
                                      'enable', 'inactive', 'HorizontalAlignment', 'left', 'BackgroundColor', [1 1 1]) ...
                            uicontrol(obj.panel, 'units', 'normalized', 'Style', 'pushbutton', ...
                                      'Position', [1/6 7/48 2/3 1/16], 'String', 'Graph', ...
                                      'BackgroundColor', [0.9 0.9 0.9], 'Callback', {@obj.graph event.Indices(1)}) ...
                            uicontrol(obj.panel, 'units', 'normalized', 'Style', 'pushbutton', ...
                                      'Position', [1/6 1/24 2/3 1/16], 'String', 'Subgraph', ...
                                      'BackgroundColor', [0.9 0.9 0.9], 'Callback', {@obj.subgraph event.Indices(1)})];
            end
        end
        
        function filter(obj, ~, ~)
        % Filter out docs that satisfies given conditions
        % This method is called when 'Search by filter' button is clicked, 
        % the user should also select a field name, a filter option and put
        % in a search string
        % obj.search(1): field name {'Select' 'Name' 'ID' 'Type' 'Date' 'Other'}
        % obj.search(2): filter options {'Filter options' 'contains' 'begins with' 'ends with'}
        % obj.search(3): search string that the user enters
        
            if (obj.search(1).Value == 1 || obj.search(2).Value == 1) && obj.search(1).Value <= 5
                msgbox(["Please choose a column name and condition to search."]);
                return
            end
            if isempty(obj.search(3).String)
                msgbox("Please enter a string")
                return
            end
            numRows = size(obj.fullTable,1);
            if obj.search(1).Value <= 5
                if obj.search(2).Value == 2
                    obj.tempTable = {};
                    obj.tempDocuments = [];
                    for i = 1:numRows
                        if contains(lower(obj.fullTable{i,obj.search(1).Value-1}), lower(obj.search(3).String))
                            obj.tempTable(end+1,:) = obj.fullTable(i,:);
                            obj.tempDocuments = [obj.tempDocuments obj.fullDocuments(i)];
                        end
                    end
                elseif obj.search(2).Value == 3
                    obj.tempTable = {};
                    obj.tempDocuments = [];
                    for i = 1:numRows
                        if startsWith(lower(obj.fullTable{i,obj.search(1).Value-1}), lower(obj.search(3).String))
                            obj.tempTable(end+1,:) = obj.fullTable(i,:);
                            obj.tempDocuments = [obj.tempDocuments obj.fullDocuments(i)];
                        end
                    end
                elseif obj.search(2).Value == 4
                    obj.tempTable = {};
                    obj.tempDocuments = [];
                    for i = 1:numRows
                        if endsWith(lower(obj.fullTable{i,obj.search(1).Value-1}), lower(obj.search(3).String))
                            obj.tempTable(end+1,:) = obj.fullTable(i,:);
                            obj.tempDocuments = [obj.tempDocuments obj.fullDocuments(i)];
                        end
                    end
                end
            else 
                contentSearch(obj, lower(obj.search(3).String), obj.table.Data)
            end
            obj.table.Data = obj.tempTable;
        end
        
        function filterHelper(obj, search1, search2, searchStr)
        % Helper for filter in case the filter function needs to be called from another class
        %
        % Usage: ndi.gui.docViewer.filterHelper(search1, search2, searchStr)
        % search1, search2 and searchStr should be three strings
        % corresponding to field obj.search(1), obj.search(2), and
        % obj.search(3) in method filter above
            
            obj.search(1).Value = search1;
            obj.search(2).Value = search2;
            obj.search(3).String = searchStr;
            obj.filter()
        end
        
        function searchID(obj, list_ID)
        % Search for documents given a list of IDs
        % list_ID: a string array containing IDs 
        
            obj.search(1).Value = 3;
            obj.search(2).Value = 2;
            obj.tempTable = {};
            obj.tempDocuments = [];
            numRows = size(obj.fullTable,1);
            for i = 1:length(list_ID)
                curr_ID = list_ID(i);
                for j = 1:numRows
                    if contains(lower(obj.fullTable{j,2}), lower(curr_ID))
                        obj.tempTable(end+1,:) = obj.fullTable(j,:);
                        obj.tempDocuments = [obj.tempDocuments obj.fullDocuments(j)];
                    end
                end
            end
            obj.table.Data = obj.tempTable;
        end
        
        function contentSearch(obj, fieldValue, data)
        % Advanced searching method, allows the user to search with
        % specific field and field value (so that the user is not limited 
        % to provided fields: 'Name' 'ID' 'Type' 'Date')
        % Helper method for filter(), this method is called when user
        % selects 'Other' for field
        
            prompt = {'Field name:'};
            dlgtitle = 'Advanced search';
            dims = [1 50];
            definput = {''};
            answer = inputdlg(prompt,dlgtitle,dims,definput);
            if isempty(answer)
                obj.table.Data = data;
                return
            end
            fieldName = lower(answer{1,1});
            obj.tempTable = {};
            obj.tempDocuments = [];
            numRows = size(obj.fullTable,1);
            for i = 1:numRows
                parent = obj.docs{i}.document_properties;
                if vlt.data.fieldsearch(parent, ...
                    struct('field',fieldName,'operation','contains_string','param1',fieldValue,'param2',''))
                    obj.tempTable(end+1,:) = obj.fullTable(i,:);
                    obj.tempDocuments = [obj.tempDocuments obj.fullDocuments(i)];
                end
            end
            obj.table.Data = obj.tempTable;
        end
                
        function searchFieldName(obj, ~, ~, fieldName)
        % Filter docs that contains a specific field without requiring any
        % contents for that field
        % This method is called when 'Search by field name' button is clicked
        
            if nargin < 4
                prompt = {'Field name:'};
                dlgtitle = 'Search field name';
                dims = [1 50];
                definput = {''};
                answer = inputdlg(prompt,dlgtitle,dims,definput);
                if isempty(answer)
                    return
                end
                fieldName = lower(answer{1,1});
            end
            
            obj.tempTable = {};
            obj.tempDocuments = [];
            numRows = size(obj.fullTable,1);
            for i = 1:numRows
                parent = obj.docs{i}.document_properties;
                if vlt.data.fieldsearch(parent, ...
                    struct('field',fieldName,'operation','hasfield','param1','','param2',''))
                    obj.tempTable(end+1,:) = obj.fullTable(i,:);
                    obj.tempDocuments = [obj.tempDocuments obj.fullDocuments(i)];
                end
            end
            obj.table.Data = obj.tempTable;
        end
        
        function clearView(obj, ~, ~)
        % Clears data of current display, full table is still stored in
        % field obj.fullTable
        % This method is called when 'Clear table' button is clicked
            obj.table.Data = {};
        end
        
        function restore(obj, ~, ~)
		% Restore view back to full table
        % This method is called when 'Restore' button is clicked
            obj.table.Data = obj.fullTable;
        end
        
        function graph(obj, ~, ~, ind)
        % Load and show graph data from a doc
            s = [];
            t = [];
            for i = 1:numel(obj.fullDocuments)
                if eq(obj.fullDocuments(i), obj.tempDocuments(ind))
                    ind = i;
                end
            end
            for i = 1:numel(obj.fullDocuments)
                if isfield(obj.fullDocuments(i).document_properties, 'depends_on')
                    depends = obj.fullDocuments(i).document_properties.depends_on;
                    for j = 1:numel(depends)
                        for k = 1:numel(obj.fullDocuments)
                            if isequal(obj.fullDocuments(k).document_properties.ndi_document.id, depends(j).value)
                                s = [s i];
                                t = [t k];
                            end
                        end
                    end
                end
            end
            figure('position', [920, 100, 480, 480], 'resize', 'off');
            ax = axes('position', [0 0 1 1]);
            % mygraph = digraph(s,t);
            % build data tips from all nodes
            % data tips could be name, type, id, creation time
            p = plot(ax, digraph(s, t), 'layout', 'layered');
            highlight(p, ind, 'NodeColor', 'r', 'MarkerSize', 6);
            set(gca, 'ydir', 'reverse');
        end
        
        function subgraph(obj, ~, ~, ind)
        % Load and show subgraph data from a doc
            s = [];
            t = [];
            for i = 1:numel(obj.fullDocuments)
                if eq(obj.fullDocuments(i), obj.tempDocuments(ind))
                    ind = i;
                    d = obj.fullDocuments(ind);
                end
            end
            for i = 1:numel(obj.fullDocuments)
                if isfield(obj.fullDocuments(i).document_properties, 'depends_on')
                    depends = obj.fullDocuments(i).document_properties.depends_on;
                    for j = 1:numel(depends)
                        if isequal(d.document_properties.ndi_document.id, depends(j).value)
                            s = [s i];
                            t = [t ind];
                        elseif eq(obj.fullDocuments(i), d)
                            for k = 1:numel(obj.fullDocuments)
                                if isequal(obj.fullDocuments(k).document_properties.ndi_document.id, depends(j).value)
                                    s = [s ind];
                                    t = [t k];
                                end
                            end
                        end
                    end
                end
            end
            g = digraph(s, t);
            d = indegree(g)+outdegree(g);
            g = rmnode(g, find(d==0));
            figure('position', [920, 100, 480, 480], 'resize', 'off');
            ax = axes('position', [0 0 1 1]);
            p = plot(ax, g, 'layout', 'layered');
            highlight(p, ind-numel(find(find(d==0)<ind)), 'NodeColor', 'r', 'MarkerSize', 6);
        end
        
    end
end
