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

% Choose a transmission (filter)
listFIL = dir(fullfile([pathTB 'filters'], '*.txt'));
c = listdlg('PromptString', 'Select a transmission:', ...
                           'SelectionMode', 'single', ...
                           'InitialValue', 1, ...
                           'ListString', {listFIL.name});
fullfil = importdata([pathTB 'filters' filesep listFIL(c).name]);
figure, plot(fullfil(:, 1), fullfil(:, 2:end))
filName = erase(listFIL(c).name, '.txt');

% Choose an observer
listOBS = dir(fullfile([pathTB 'observers'], '*.txt'));
c = listdlg('PromptString', 'Select an observer:', ...
                           'SelectionMode', 'single', ...
                           'InitialValue', 4, ...
                           'ListString', {listOBS.name});
fullCMFs = importdata([pathTB 'observers' filesep listOBS(c).name]);
figure, plot(fullCMFs(:, 1), fullCMFs(:, 2:end))
obsName = erase(listOBS(c).name, '.txt');

% Choose a destination RGB space
listDCS = dir(fullfile([pathTB 'colorSpaces_ICC'], '*.icc'));
c = listdlg('PromptString', 'Select a destination RGB space:', ...
                           'SelectionMode', 'single', ...
                           'InitialValue', 3, ...
                           'ListString', {listDCS.name});
DCS = iccread([pathTB 'colorSpaces_ICC' filesep listDCS(c).name]);
DCSname = erase(listDCS(c).name, '.icc');

%% Calculate the RGB2XYZ transformation matrix

wtP = DCS.Header.Illuminant';
gamma = DCS.MatTRC.GreenTRC.Params;
redChr = DCS.MatTRC.RedMatrixColumn';
greenChr = DCS.MatTRC.GreenMatrixColumn';
blueChr = DCS.MatTRC.BlueMatrixColumn';

R_x = redChr(1) / sum(redChr);
R_y = redChr(2) / sum(redChr);
G_x = greenChr(1) / sum(greenChr);
G_y = greenChr(2) / sum(greenChr);
B_x = blueChr(1) / sum(blueChr);
B_y = blueChr(2) / sum(blueChr);

S = [(R_x/R_y) (G_x/G_y) (B_x/B_y); 1 1 1; ...
    ((1-R_x-R_y)/R_y) ((1-G_x-G_y)/G_y) ((1-B_x-B_y)/B_y)] \ wtP;
RGBtoXYZ = [S(1)*(R_x/R_y) S(2)*(G_x/G_y) S(3)*(B_x/B_y); S(1) S(2) S(3); ...
    S(1)*((1-R_x-R_y)/R_y) S(2)*((1-G_x-G_y)/G_y) S(3)*((1-B_x-B_y)/B_y)];

%% Calculation of the RGB images (with and without filter)

fprintf('Importing captured MS cube...\n')
% Load hyperspectral cube
hcube = load([pathCB headCB]).hsi;
CUBE = hcube(:,:,1:endvis); % if the cube is float in [0 1]
%CUBE = double(hcube.DataCube)(:,:,1:endvis)/roof; % if the cube is uint16
bands = linspace(400, 1000, 160)';
bands = bands(1:endvis);
dims = size(CUBE);
clc

min_value = min(CUBE(:));
max_value = max(CUBE(:));
disp(['Min value: ', num2str(min_value), ', Max value: ', num2str(max_value)]);

min_wavelength = min(bands);
max_wavelength = max(bands);
disp(['Min wavelength: ', num2str(min_wavelength), ', Max wavelength: ', num2str(max_wavelength)]);

% Reshape the cube
lincube = reshape(CUBE, [], size(bands, 1));

% Interpolate the illuminant and observer data
ill = interp1(fullill(:, 1), fullill(:, 2), bands, 'spline');
CMFs_x = interp1(fullCMFs(:, 1), fullCMFs(:, 2), bands, 'spline');
CMFs_y = interp1(fullCMFs(:, 1), fullCMFs(:, 3), bands, 'spline');
CMFs_z = interp1(fullCMFs(:, 1), fullCMFs(:, 4), bands, 'spline');
CMFs = [CMFs_x CMFs_y CMFs_z];

% Calculate tristimulus reference
sp_tristREF = CMFs .* ill;
tristREF = sum(sp_tristREF, 1);

% 1. Without Filter
trist_no_filter = double(lincube) * double(sp_tristREF);
linRGB_no_filter = (RGBtoXYZ \ trist_no_filter') ./ max(RGBtoXYZ \ tristREF');
RGB_gamma_no_filter = linRGB_no_filter .^ (1 / gamma);
imRGB_no_filter = (reshape(RGB_gamma_no_filter', dims(1), dims(2), 3)) * double(intmax('uint16'));

filename_no_filter = [erase(headCB, '.hdr') '_' illName '.tif'];
imwrite(uint16(imRGB_no_filter), [pathCB filesep filename_no_filter], 'tif');

% 2. With Filter
fil = interp1(fullfil(:, 1), fullfil(:, 2), bands, 'spline');
lincube_filtered = (lincube' .* fil)';

trist_with_filter = double(lincube_filtered) * double(sp_tristREF);
linRGB_with_filter = (RGBtoXYZ \ trist_with_filter') ./ max(RGBtoXYZ \ tristREF');
RGB_gamma_with_filter = linRGB_with_filter .^ (1 / gamma);
imRGB_with_filter = (reshape(RGB_gamma_with_filter', dims(1), dims(2), 3)) * double(intmax('uint16'));

filename_with_filter = [erase(headCB, '.hdr') '_' illName '_N_Filtered' '.tif'];
imwrite(uint16(imRGB_with_filter), [pathCB filesep filename_with_filter], 'tif');
