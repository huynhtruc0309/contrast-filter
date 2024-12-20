clc; clear; close all

pathTB = [pwd filesep 'tools' filesep];

roof = double(intmax('uint16'));

endvis = 117;

%% Get cube and other data

% Choose a folder with HDR files
hdrPath = uigetdir(pathTB, 'Select folder with HDR files');
listHDRs = dir(fullfile(hdrPath, '*.hdr'));

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

% Choose a folder with filter files
filterPath = uigetdir(pathTB, 'Select folder with filter txt files');
listFilters = dir(fullfile(filterPath, '*.txt'));

%% Process each HDR file

for j = 1:length(listHDRs)
    headCB = listHDRs(j).name;
    pathCB = listHDRs(j).folder;

    %% Calculation of the RGB image

    fprintf('Importing captured MS cube...')
    hcube = hypercube(fullfile(pathCB, headCB));
    CUBE = double(hcube.DataCube(:,:,1:endvis));
    CUBE = (CUBE - min(CUBE(:))) / (max(CUBE(:)) - min(CUBE(:))); % Normalize CUBE to [0, 1]
    bands = hcube.Wavelength(1:endvis);
    dims = size(CUBE);
    clc

    fprintf('Max CUBE value: %f\n', max(CUBE(:)));
    fprintf('Min CUBE value: %f\n', min(CUBE(:)));

    lincube = reshape(CUBE,[],size(bands,1));

    CMFs_x = interp1(fullCMFs(:,1),fullCMFs(:,2),bands,'spline');
    CMFs_y = interp1(fullCMFs(:,1),fullCMFs(:,3),bands,'spline');
    CMFs_z = interp1(fullCMFs(:,1),fullCMFs(:,4),bands,'spline');
    CMFs = [CMFs_x CMFs_y CMFs_z];

    trist = double(lincube) * double(CMFs);

    linRGB = (RGBtoXYZ\trist')./max(RGBtoXYZ\sum(CMFs,1)');

    % Inspect intermediate values
    fprintf('Max linRGB value: %f\n', max(linRGB(:)));
    fprintf('Min linRGB value: %f\n', min(linRGB(:)));

    RGB_gamma = linRGB.^(1/gamma);

    % Inspect intermediate values after gamma correction
    fprintf('Max RGB_gamma value: %f\n', max(RGB_gamma(:)));
    fprintf('Min RGB_gamma value: %f\n', min(RGB_gamma(:)));

    imRGB = (reshape(RGB_gamma',dims(1),dims(2),3))*double(intmax('uint16'));

    % Ensure final image values are clamped within [0, intmax('uint16')]
    imRGB = max(0, min(imRGB, double(intmax('uint16'))));

    filename_no_filter = [erase(headCB,'.hdr') '_no_filter.png'];
    imwrite(uint16(imRGB),[pathCB filesep filename_no_filter],'png');

    %% Apply filters

    for i = 1:length(listFilters)
        fullfil = importdata(fullfile(filterPath, listFilters(i).name));
        fil = interp1(fullfil(:, 1), fullfil(:, 2), bands, 'spline');

        % Apply filter to CUBE
        lincube_filtered = (lincube' .* fil)';
        
        % Recalculate RGB image with filtered data
        trist_filtered = double(lincube_filtered) * double(CMFs);
        linRGB_filtered = (RGBtoXYZ\trist_filtered')./max(RGBtoXYZ\sum(CMFs,1)');
        linRGB_filtered = max(0, min(linRGB_filtered, 1));
        RGB_gamma_filtered = linRGB_filtered.^(1/gamma);
        imRGB_filtered = (reshape(RGB_gamma_filtered', dims(1), dims(2), 3)) * double(intmax('uint16'));
        imRGB_filtered = max(0, min(imRGB_filtered, double(intmax('uint16'))));
        
        % Save filtered image
        filterName = erase(listFilters(i).name, '.txt');
        filename_filtered = [erase(headCB,'.hdr') '_RGB_' filterName '.png'];
        imwrite(uint16(imRGB_filtered), [pathCB filesep filename_filtered], 'png');
    end
end
