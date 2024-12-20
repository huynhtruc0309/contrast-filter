
clc; clear; close all

pathTB = [pwd filesep 'tools' filesep];

roof = double(intmax('uint16'));

endvis = 117;

%% Get cube and other data

% locate cube
f = msgbox('Select the header of the spectral cube');
movegui(f,'northwest')
pause(1)
[headCB,pathCB] = uigetfile('*.mat');
close(f)

% Choose an illuminant
listILL = dir(fullfile([pathTB 'sources'],'*.txt'));
c = listdlg('PromptString','Select an illuminant:',...
                           'SelectionMode','single',...
                           'InitialValue',4, ...
                           'ListString',{listILL.name});
fullill = importdata([pathTB 'sources' filesep listILL(c).name]);
figure,plot(fullill(:,1),fullill(:,2:end))
illName = erase(listILL(c).name,'.txt');

% Choose an observer
listOBS = dir(fullfile([pathTB 'observers'],'*.txt'));
c = listdlg('PromptString','Select an observer:',...
                           'SelectionMode','single',...
                           'InitialValue',4, ...
                           'ListString',{listOBS.name});
fullCMFs = importdata([pathTB 'observers' filesep listOBS(c).name]);
figure,plot(fullCMFs(:,1),fullCMFs(:,2:end))
obsName = erase(listOBS(c).name,'.txt');

% Choose a destination RGB space
listDCS = dir(fullfile([pathTB 'colorSpaces_ICC'],'*.icc'));
c = listdlg('PromptString','Select a destination RGB space:',...
                           'SelectionMode','single',...
                           'InitialValue',3, ...
                           'ListString',{listDCS.name});
DCS = iccread([pathTB 'colorSpaces_ICC' filesep listDCS(c).name]);
DCSname = erase(listDCS(c).name,'.icc');

%% Calculate the RGB2XYZ transformation matrix

wtP = DCS.Header.Illuminant';
gamma = DCS.MatTRC.GreenTRC.Params;
redChr = DCS.MatTRC.RedMatrixColumn';
greenChr = DCS.MatTRC.GreenMatrixColumn';
blueChr = DCS.MatTRC.BlueMatrixColumn';

R_x = redChr(1)/sum(redChr);
R_y = redChr(2)/sum(redChr);
G_x = greenChr(1)/sum(greenChr);
G_y = greenChr(2)/sum(greenChr);
B_x = blueChr(1)/sum(blueChr);
B_y = blueChr(2)/sum(blueChr);

S = [(R_x/R_y) (G_x/G_y) (B_x/B_y); 1 1 1; ...
    ((1-R_x-R_y)/R_y) ((1-G_x-G_y)/G_y) ((1-B_x-B_y)/B_y)] \ wtP;
RGBtoXYZ = [S(1)*(R_x/R_y) S(2)*(G_x/G_y) S(3)*(B_x/B_y); S(1) S(2) S(3); ...
    S(1)*((1-R_x-R_y)/R_y) S(2)*((1-G_x-G_y)/G_y) S(3)*((1-B_x-B_y)/B_y)];

%% calculation of the RGB image

fprintf('Importing captured MS cube...\n')
% hcube = hypercube([pathCB headCB]);
hcube = load([pathCB headCB]).hsi;
CUBE = hcube(:,:,1:endvis); % if the cube is float in [0 1]
%CUBE = double(hcube.DataCube)(:,:,1:endvis)/roof; % if the cube is uint16
bands = linspace(400, 1000, 160)';
bands = bands(1:endvis);
dims = size(CUBE);
clc

lincube = reshape(CUBE,[],size(bands,1));

fprintf('Max lincube value: %f\n', max(lincube(:)));
fprintf('Min lincube value: %f\n', min(lincube(:)));

ill = interp1(fullill(:,1),fullill(:,2),bands,'spline');

CMFs_x = interp1(fullCMFs(:,1),fullCMFs(:,2),bands,'spline');
CMFs_y = interp1(fullCMFs(:,1),fullCMFs(:,3),bands,'spline');
CMFs_z = interp1(fullCMFs(:,1),fullCMFs(:,4),bands,'spline');
CMFs = [CMFs_x CMFs_y CMFs_z];

sp_tristREF = CMFs.*ill;
tristREF = sum(sp_tristREF,1);

trist = double(lincube) * double(sp_tristREF);

linRGB = (RGBtoXYZ\trist')./max(RGBtoXYZ\tristREF'); % <RGBtoXYZ\trist'> is better than <inv(RGBtoXYZ)*trist'>

fprintf('Max linRGB value: %f\n', max(linRGB(:)));
fprintf('Min linRGB value: %f\n', min(linRGB(:)));

RGB_gamma = linRGB.^(1/gamma);

imRGB = (reshape(RGB_gamma',dims(1),dims(2),3))*double(intmax('uint16'));

fprintf('Max imRGB value: %f\n', max(imRGB(:)));
fprintf('Min imRGB value: %f\n', min(imRGB(:)));

filename = [erase(headCB,'.hdr') '_' illName '.tif'];

imwrite(uint16(imRGB),[pathCB filesep filename],'tif')
