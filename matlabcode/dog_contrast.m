function dog_contrast = dog_contrast(img)
    img = double(img);
    sigma1 = 1;
    sigma2 = 3;
    g1 = imgaussfilt(img, sigma1);
    g2 = imgaussfilt(img, sigma2);
    dog_contrast = std(g1(:) - g2(:));
end