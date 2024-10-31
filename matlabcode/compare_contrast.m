function compare_contrast(original_img_path, filtered_img_path)
    % Load the images
    original_img = imread(original_img_path);
    filtered_img = imread(filtered_img_path);

    % Convert to grayscale for luminance-based contrast measures
    original_gray = rgb2gray(original_img);
    filtered_gray = rgb2gray(filtered_img);

    % Global Contrast Measures
    disp('Global Contrast Measures:');
    
    % 1. Maximum to Minimum Luminance Ratio
    fprintf('Max-Min Luminance Ratio - Original: %.2f\n', max_min_ratio(original_gray));
    fprintf('Max-Min Luminance Ratio - Filtered: %.2f\n\n', max_min_ratio(filtered_gray));
    
    % 2. Weber Contrast
    fprintf('Weber Contrast - Original: %.2f\n', weber_contrast(original_gray));
    fprintf('Weber Contrast - Filtered: %.2f\n\n', weber_contrast(filtered_gray));
    
    % 3. Michelson Contrast
    fprintf('Michelson Contrast - Original: %.2f\n', michelson_contrast(original_gray));
    fprintf('Michelson Contrast - Filtered: %.2f\n\n', michelson_contrast(filtered_gray));
    
    % 4. Root-Mean-Square (RMS) Contrast
    fprintf('RMS Contrast - Original: %.2f\n', rms_contrast(original_gray));
    fprintf('RMS Contrast - Filtered: %.2f\n\n', rms_contrast(filtered_gray));
    
    % 5. Single Image Perceived Contrast (SIPk)
    fprintf('SIPk - Original: %.2f\n', calculate_SIPk(original_img));
    fprintf('SIPk - Filtered: %.2f\n\n', calculate_SIPk(filtered_img));

    % Local Contrast Measures
    disp('Local Contrast Measures:');
    
    % 6. Difference of Gaussians (DoG)
    fprintf('DoG Contrast - Original: %.2f\n', dog_contrast(original_gray));
    fprintf('DoG Contrast - Filtered: %.2f\n\n', dog_contrast(filtered_gray));

    % 7. Local Mean Differences
    fprintf('Local Mean Differences - Original: %.2f\n', local_mean_diff(original_gray));
    fprintf('Local Mean Differences - Filtered: %.2f\n\n', local_mean_diff(filtered_gray));

    % 8. Peli’s Local Band-Limited Contrast
    fprintf('Peli Local Band-Limited Contrast - Original: %.2f\n', peli_contrast(original_gray));
    fprintf('Peli Local Band-Limited Contrast - Filtered: %.2f\n\n', peli_contrast(filtered_gray));

    % 9. Just Noticeable Differences (JND)
    fprintf('JND - Original: %.2f\n', calculate_JND(original_gray));
    fprintf('JND - Filtered: %.2f\n\n', calculate_JND(filtered_gray));

    % Contrast Sensitivity Function
    disp('Contrast Sensitivity Function (CSF):');
    plot_CSF_comparison(original_gray, filtered_gray);
end
