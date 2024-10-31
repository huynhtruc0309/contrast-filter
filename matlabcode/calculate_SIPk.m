function SIPk = calculate_SIPk(img)
    lab_img = rgb2lab(img);
    L_channel = lab_img(:,:,1);
    a_channel = lab_img(:,:,2);
    b_channel = lab_img(:,:,3);
    chroma = sqrt(a_channel.^2 + b_channel.^2);
    sigma2 = 5;
    lowpass_L = imgaussfilt(L_channel, sigma2);
    highpass_L = L_channel - lowpass_L;
    k_C = std(chroma(:));
    k_L = std(L_channel(:));
    k_S = std(highpass_L(:));
    SIPk = -1.505 + 0.131 * k_C + 0.151 * k_L + 666.216 * k_S;
end