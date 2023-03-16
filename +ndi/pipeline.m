% a) Ready for review: Make the window only about half its height by shrinking the height of the list of calculators
% b) TODO: Make the list a uitable with the following entries: calculator, I, and O 
%    (I is short for number of inputs, O is short for number of outputs). 
%    Initially you can leave the I and O blank. Add a new button called refresh that will run 
%    code to count the number of input and output documents for the calculator (I can fill in that code).
% Problem: Cell selection
% c) Ready for review: Move the buttons that operate on the pipelines to be just below the popup menu for the pipelines (see drawing)
% d) Ready for review: Move the buttons that operate on calculators to the bottom of the former list/ uitable

classdef pipeline

	% A class for managing pipelines of ndi.calculator objects in NDI.
	%
	%
	% To test and for a demo, use
	%
	%	ndi.test.pipeline.editpipeline()
        
		properties (SetAccess=protected,GetAccess=public)

		end % properties
    
        methods
		end % methods
    
		methods (Static)
			function edit(varargin)
				% ndi.pipeline.edit - create and control a GUI to graphically edit a PIPELINE EDITOR instance
				%
				% ndi.pipeline.edit (...)
				%
				% Creates and controls a graphical user interface for creating an instance of
				% an pipeline.editor object.
				% 
				% Usage by the user:
				%
				%   S = []; % use an empty session for now
				%   ndi.pipeline.edit('command','new','pipelinePath',fullfile(userpath,'tools','NDI-matlab','+ndi','+test','+pipeline','test_pipeline'),'session',S);
				%
				%
					session = []; % start with a blank session
					vlt.data.assign(varargin{:});
			
					window_params.height = 500;
					window_params.width = 400;
                    
					fig = []; % figure to use

					if strcmpi(command,'new'), 
						if isempty(fig),
							fig = uifigure;
						end;
                        keyboard
						command = 'NewWindow';
						% new window, set userdata
						if exist('pipelinePath','var'),
							% is it a valid directory?
							if isfolder(pipelinePath),
								ud.pipelinePath = pipelinePath;
								ud.pipelineList = []; % initially empty
								ud.pipelineListChar = []; % initially empty
								ud.session = session;
								set(fig,'userdata',ud);
							else,
								error(['The provided pipeline path does not exist: ' pipelinePath '.']);
							end;
						else,
							error(['No pipelinePath provided.']);
						end;
					else 
						fig = gcf;
						% not new window, get userdata
						ud = get(fig,'userdata'),
					end;
			
					if isempty(fig),
						error(['Empty figure, do not know what to work on.']);
					end;
			
					disp(['Command is ' command '.']);
				       
					switch (command),
						case 'NewWindow',
							set(fig,'tag','ndi.pipeline.edit');  

							uid = vlt.ui.basicuitools_defs;
				
							callbackstr = [  'eval([get(gcbf,''Tag'') ''(''''command'''','''''' get(gcbo,''Tag'') '''''' ,''''fig'''',gcbf);'']);']; 

							% Step 1: Establish window geometry
                            
							top = 1; % 1 is 100% in normalized unit
							right = 1; % 1 is 100% in normalized unit
							row = top/20; % 20 rows
							edge = right/40; % 1/40 edge on each side
                            x = edge; % real x for uicontrol, because we need to leave an edge
                            y = top-edge; % real y for uicontrol, because we need to leave an edge
                            
                            title_height = row;
							title_width = right-2*edge;
                            
							doc_width = right-2*edge;
							doc_height = 7*row;
                            doc_column_width = {200, 75, 75};
                            
							menu_width = right-2*edge;
							menu_height = title_height;
                            
							button_width = right/4;
							button_height = row;
                            
                            pipeline_buttons_txt = y-13*row;
                            pipeline_buttons_x = [edge right/2-1/2*button_width (right-button_width-edge)];
                            pipeline_buttons_y = y-14*row;
                            
                            calculator_buttons_txt = y-16*row;
                            calculator_buttons_x = [edge right/2-1/2*button_width (right-button_width-edge)];
                            calculator_buttons_y = y-17*row;

							% Step 2 now build it
						
							set(fig,'position',[50 50 window_params.width window_params.height]);
							set(fig,'NumberTitle','off');
							set(fig,'Name',['Editing ' ud.pipelinePath]);
				    
							% Pipeline selection portion of window
							uicontrol(uid.txt,'units','normalized','position',[x y-title_height title_width title_height],'string','Select pipeline:','tag','PipelineTitleTxt');
							uicontrol(uid.popup,'units','normalized','position',[x y-2*title_height menu_width menu_height],...
								'string',ud.pipelineListChar,'tag','PipelinePopup','callback',callbackstr);
                            
                            % Pipeline menu portion
                            uicontrol(uid.txt,'units','normalized','position',[x y-4*title_height title_width title_height],'string','Pipeline menu:','tag','PipelineMenuTxt');
                            %uicontrol(uid.edit,'units', 'normalized', 'style','listbox','position',[x y-4*title_height-doc_height doc_width doc_height],...
							%	'string',{'Please select or create a pipeline.'},...
							%	'tag','PipelineContentList','min',0,'max',2,'callback',callbackstr); 
                            uitable('units', 'normalized', 'position',[x y-4*title_height-doc_height doc_width doc_height],...
                                'ColumnName', {'Calculator'; 'I'; 'O'}, ...
                                'ColumnWidth', doc_column_width, ...
                                'Data', {}, ...
                                'tag','PipelineContentList',...
                                'CellSelectionCallback', callbackstr);
                            
                            % Pipeline operation buttons portion
                            uicontrol(uid.txt,'units','normalized','position',[x pipeline_buttons_txt title_width title_height],'string','Pipeline operations:','tag','PipelineOpeTxt');
							uicontrol(uid.button,'units', 'normalized', 'position',[pipeline_buttons_x(1) pipeline_buttons_y button_width button_height],...
								'string','+','tag','NewPipelineBt','Tooltipstring','Create new pipeline',...
								'callback',callbackstr);
							uicontrol(uid.button,'units','normalized','position',[pipeline_buttons_x(2) pipeline_buttons_y button_width button_height],...
								'string','-','Tooltipstring','Delete Current Pipeline','tag','DltPipelineBt',...
								'callback',callbackstr);
                            uicontrol(uid.button,'units','normalized','position',[pipeline_buttons_x(3) pipeline_buttons_y button_width button_height],...
								'string','->','tag','RunBt','callback',callbackstr,'Tooltipstring','Run pipeline calculations in order');
                            
                            % Calculator operation buttons portion
                            uicontrol(uid.txt,'units','normalized','position',[x calculator_buttons_txt title_width title_height],'string','Calculator operations:','tag','CalculatorOpeTxt');
							uicontrol(uid.button,'units','normalized','position',[calculator_buttons_x(1) calculator_buttons_y button_width button_height],...
								'string','+','Tooltipstring','Create New Calculator','tag','NewCalcBt',...
								'callback',callbackstr);
							uicontrol(uid.button,'units','normalized','position',[calculator_buttons_x(2) calculator_buttons_y button_width button_height],...
								'string','-','Tooltipstring','Delete Current Calculator','tag','DltCalcBt','callback',callbackstr);
							uicontrol(uid.button,'units','normalized','position',[calculator_buttons_x(3) calculator_buttons_y button_width button_height],...
								'string','Edit','tooltipstring','Edit selected calculator','tag','EditBt','callback',callbackstr);
							ndi.pipeline.edit('command','LoadPipelines'); % load the pipelines from disk
				
						case 'UpdatePipelines', % invented command that is not a callback
							ud.pipelineList = ndi.pipeline.getPipelines(ud.pipelinePath);
							ud.pipelineListChar = ndi.pipeline.pipelineListToChar(ud.pipelineList);
							set(fig,'userdata',ud);
							
						case 'LoadPipelines', % invented command that is not a callback
							% called on startup or if the user ever changes the file path through some future mechanism
							ud.pipelineList = ndi.pipeline.getPipelines(ud.pipelinePath);
							ud.pipelineListChar = ndi.pipeline.pipelineListToChar(ud.pipelineList);
							set(fig,'userdata',ud);
							pipelinePopupObj = findobj(fig,'tag','PipelinePopup');
							index = 1;
							if exist('selectedPipeline','var')
							    index = find(strcmp(selectedPipeline,ud.pipelineListChar));
							end
							set(pipelinePopupObj, 'string',ud.pipelineListChar,'Value',index);
							pipelineContentObj = findobj(fig,'tag','PipelineContentList');
							if index == 1
								% set(pipelineContentObj, 'string', [], 'Value', 1);
                                set(pipelineContentObj, 'Data', {});
							else
								calcList = ndi.pipeline.getCalcFromPipeline(ud.pipelineList, ud.pipelineListChar{index});
								calcListChar = ndi.pipeline.calculationsToChar(calcList);
								pipelineContentObj = findobj(fig,'tag','PipelineContentList');
% 								set(pipelineContentObj, 'string', calcListChar, 'Value', min(numel(calcListChar),1));
                                set(pipelineContentObj, 'Data', [calcListChar', repmat({''}, length(calcListChar), 2)]);
							end
							
						case 'UpdateCalculatorList', % invented command that is not a callback
							calcList = ndi.pipeline.getCalcFromPipeline(ud.pipelineList, pipeline_name);
							calcListChar = ndi.pipeline.calculationsToChar(calcList);
							pipelineContentObj = findobj(fig,'tag','PipelineContentList');
% 							set(pipelineContentObj, 'string', calcListChar, 'Value', min(numel(calcListChar),1));
                            set(pipelineContentObj, 'Data', [calcListChar', repmat({''}, length(calcListChar), 2)]);
				
						case 'PipelinePopup',
							% Step 1: search for the objects you need to work with
							pipelinePopupObj = findobj(fig,'tag','PipelinePopup');
							val = get(pipelinePopupObj, 'value');
							str = get(pipelinePopupObj, 'string');
							% Step 2, check not the "---" one and display
							if val == 1
								msgbox('Please select or create a pipeline.');
								pipelineContentObj = findobj(fig,'tag','PipelineContentList');
% 								set(pipelineContentObj, 'string', [], 'Value', 1);
                                set(pipelineContentObj, 'Data', {});
								return
							end
							pipeline_name = str{val};
							ndi.pipeline.edit('command','UpdateCalculatorList','pipeline_name',pipeline_name); 
				
						case 'NewPipelineBt',
							% get dir
							read_dir = [ud.pipelinePath filesep];
							% create dialog box
							defaultfilename = {['untitled']};
							prompt = {'Pipeline name:'};
							dlgtitle = 'Save new pipeline';
							extension_list = {['']};
							% check if the user want to create/replace
							[success,filename,replaces] = ndi.util.choosefileordir(read_dir, prompt, defaultfilename, dlgtitle, extension_list);
							if success % if success, add pipeline
								if replaces
									rmdir([read_dir filesep filename], 's');
								end
								mkdir(read_dir,filename);
								% update and load pipelines
								ndi.pipeline.edit('command','LoadPipelines','selectedPipeline',filename);
							end
						
						case 'DltPipelineBt',
							pipelinePopupObj = findobj(fig,'tag','PipelinePopup');
							val = get(pipelinePopupObj, 'value');
							% check not the "---" 
							if val == 1
								msgbox('Please select a pipeline to delete.');
                                return
							end
							str = get(pipelinePopupObj, 'string');
							% get dir
							read_dir = [ud.pipelinePath filesep];  
							filename = str{val};
							% ask and delete
							msgBox = sprintf('Do you want to delete this pipeline?');
							title = 'Delete file';
							b = questdlg(msgBox, title, 'Yes', 'No', 'Yes');
							if strcmpi(b, 'Yes')
								rmdir([read_dir filesep filename], 's');
                            end
                            % update and load pipelines
							ndi.pipeline.edit('command','LoadPipelines');
				
						case 'NewCalcBt',
							pipelinePopupObj = findobj(fig,'tag','PipelinePopup');
										val = get(pipelinePopupObj, 'value');
							% check not the "---" 
							if val == 1
								msgbox('Please select or create a pipeline.');
								return;
							end
							str = get(pipelinePopupObj, 'string');
							pipeline_name = str{val};
							
							% get calculator type
							calcTypeList = {'ndi.calc.not_finished_yet','ndi.calc.need_calculator_types','ndi.calc.this_is_a_placeholder'};
							[calcTypeStr,calcTypeVal] = listdlg('PromptString','Choose a calculator type:',...
								'SelectionMode','single','ListString',calcTypeList);
							if (calcTypeVal == 0) % check selection
								return
							end
							calculator = calcTypeList{calcTypeStr};
							
							% ask for file name
							read_dir = [ud.pipelinePath filesep pipeline_name filesep];
							prompt = {'Calculator name:'};
							dlgtitle = 'Create new calculator';
							defaultfilename = {['untitled']};
							extension_list = {['.json']};
							[success,calcname,replaces] = ndi.util.choosefileordir(read_dir, prompt, defaultfilename, dlgtitle, extension_list);
							if success % if success, create and save newCalc
								if replaces
									delete([read_dir filesep calcname '.json']);
								end
								newCalc = ndi.pipeline.setDefaultCalc(calculator, calcname);
								json_filename = char(strcat(read_dir,calcname,'.json'));
								fid = fopen(json_filename,'w');
								fprintf(fid,jsonencode(newCalc));
								fclose(fid);
								% update and load calculator
								ndi.pipeline.edit('command','UpdatePipelines');
								ndi.pipeline.edit('command','UpdateCalculatorList','pipeline_name',pipeline_name);
							end
				
						case 'DltCalcBt',
							pipelinePopupObj = findobj(fig,'tag','PipelinePopup');
							pip_val = get(pipelinePopupObj, 'value');
							% check not the "---" 
							if pip_val == 1
								msgbox('Please select or create a pipeline.');
								return;
							end
							pip_str = get(pipelinePopupObj, 'string');
							msgBox = sprintf('Do you want to delete this calculator?');
							title = 'Delete calculator';
							b = questdlg(msgBox, title, 'Yes', 'No', 'Yes');
							if strcmpi(b, 'Yes');
								pipeline_name = pip_str{pip_val};
								piplineContentObj = findobj(fig,'tag','PipelineContentList')
								calc_val = get(piplineContentObj, 'value')
								calc_str = get(piplineContentObj, 'string')
								calc_name = calc_str{calc_val};
								filename = [ud.pipelinePath filesep pipeline_name filesep calc_name '.json'];  
								delete(filename);
								% update and load pipelines
								ndi.pipeline.edit('command','UpdatePipelines');
								ndi.pipeline.edit('command','UpdateCalculatorList','pipeline_name',pipeline_name); 
							end
						case 'EditBt'
							pipelinePopupObj = findobj(fig,'tag','PipelinePopup');
							pip_val = get(pipelinePopupObj, 'value');
							% check not the "---" 
							if pip_val == 1
								msgbox('Please select or create a pipeline.');
								return;
							end
							pip_str = get(pipelinePopupObj, 'string');
							pipeline_name = pip_str{pip_val};
							piplineContentObj = findobj(fig,'tag','PipelineContentList');
							calc_val = get(piplineContentObj, 'value');
							calc_str = get(piplineContentObj, 'string');
							calc_name = calc_str{calc_val};
							% replace illegal chars to underscore
							calc_name = regexprep(calc_name,'[^a-zA-Z0-9]','_');
							full_calc_name = [ud.pipelinePath filesep pipeline_name filesep calc_name '.json'];
							ndi.calculator.graphical_edit_calculator('command','EDIT','filename',full_calc_name,'session',ud.session);
						case 'RunBt'
							disp([command 'is not implemented yet.']);
						case 'PipelineContentList'
							disp([command 'is not supposed to do anything.'])
						otherwise,
							disp(['Unknown command ' command '.']);
					end; % switch(command)

			end % pipeline_edit()
        
        function getCellValue(src, evt)
            row = evt.Indices(1);
            col = evt.Indices(2);
            value = src.Data{row, col};
            disp(value);
        end
        
		function calcList = getCalcFromPipeline(pipelineList, pipeline_name)
			%
			% ndi.pipeline.getCalcFromPipeline - read a CALCLIST from PIPELINELIST
			%
			% CALCLIST = ndi.pipeline.getCalcFromPipeline(PIPELINELIST, PIPELINE_NAME)
			%
			% Input: 
			%   PIPELINELIST: a list of pipelines
			%   PIPELINE_NAME: a name string of a specific pipeline in this pipeline list
			% Output: 
			%   CALCLIST: a list of calculators
			% 
				calcList = [];
				for i = 1:length(pipelineList)
					if strcmp(pipelineList{i}.pipeline_name, pipeline_name)
						calcList = pipelineList{i}.calculations;
					end
				end
		end % getCalcFromPipeline
            
		function calcListChar = calculationsToChar(calcList)
			%
			% ndi.pipeline.calculationsToChar - read names of a CALCLIST as a list of strings
			%
			% CALCLISTCHAR = ndi.pipeline.calculationsToChar(CALCLIST)
			% 
			% Input: 
			%   CALCLIST: a list of calculators
			% Output: 
			%   CALCLISTCHAR: a list of strings, representing names of calculators in CALCLIST
			% 

				calcListChar = [];
				for i = 1:length(calcList)
					calcListChar{i} = calcList{i}.ndi_pipeline_element.name;
				end
		end % calculationsToChar
            
		function newCalc = setDefaultCalc(calculator, name)
			%
			% ndi.pipeline.setDefaultCalc - set default parameters for a new calculator
			%
			% NEWCALC = ndi.pipeline.setDefaultCalc(CALCULATOR, NAME)
			% 
			% Input
			%   CALCULATOR: a type of calculator (EXAMPLE: ndi.calc.stimulus.tuningcurve)
			%   NAME: a name string of calculator
			% Output: 
			%   NEWCALC: a new calculator created by this function
			% 
				newCalc.ndi_pipeline_element.calculator = calculator;
				newCalc.ndi_pipeline_element.name = name;
				newCalc.ndi_pipeline_element.filename = name;
				newCalc.ndi_pipeline_element.parameter_code = '';
				newCalc.ndi_pipeline_element.default_options = containers.Map("if_document_exists_do","NoAction");
		end % setDefaultCalc
            
		function pipelineList = getPipelines(read_dir)
			%
			% ndi.pipeline.getPipelines - read a PIPELINE_LIST from directory READ_DIR
			%
			% PIPELINELIST = ndi.pipeline.getPipelines(READ_DIR)
			% 
			% Input: 
			%   READ_DIR: a directory where the pipelines are stored as a PIPELINE_LIST
			% Output: 
			%   PIPELINELIST: a list of pipelines
			% 
				d = dir(read_dir);
				isub = [d(:).isdir]; 
				nameList = {d(isub).name}';
				nameList(ismember(nameList,{'.','..'})) = [];
				pipelineList{1}.pipeline_name = '---';
				pipelineList{1}.calculations = {};
				for i = 2:(length(nameList)+1)
					pipelineList{i}.pipeline_name = nameList{i-1};
					pipelineList{i}.calculations = {};
					D = dir([read_dir filesep char(pipelineList{i}.pipeline_name) filesep '*.json']);
					for d = 1:numel(D),
						%D(d).name is the name of the nth calculator in the pipeline; you can use that to build your list of calculators
						pipelineList{i}.calculations{d} = jsondecode(vlt.file.textfile2char([read_dir filesep char(pipelineList{i}.pipeline_name) filesep D(d).name]));
					end
				end
		end % getPipelines

		function pipelineListChar = pipelineListToChar(pipelineList)
			%
			% ndi.pipeline.pipelineListToChar - read names of a PIPELINELIST as a list of strings
			%
			% PIPELINELISTCHAR = ndi.pipeline.pipelineListToChar(PIPELINELIST)
			% 
			% Input: 
			%   PIPELINELIST: a list of pipelines
			% Output: 
			%   PIPELINELISTCHAR: a list of strings, representing names of pipelines in PIPELINELIST
			% 
				pipelineListChar = [];
				for i = 1:length(pipelineList)
				    pipelineListChar{i} = pipelineList{i}.pipeline_name;
				end
		end % pipelineListToChar
        
        %}
 
	end % static methods
end % class

