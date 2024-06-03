function numObjects = face_collection(imagePath)
    % 读取图像
    image = imread(imagePath);

    % 图像预处理
    grayImage = rgb2gray(image);
    binaryImage = imbinarize(grayImage);

    % 形态学处理
    se1 = strel('disk', 13); % 结构元素大小为13
    se2 = strel('disk', 4); % 结构元素大小为4
    binaryImage = imopen(binaryImage, se1); % 开运算
    binaryImage = imclose(binaryImage, se2); % 闭运算

    % 标记对象并计数
    cc = bwconncomp(binaryImage);

    % 过滤小目标
    minObjectSize = 100; % 设定最小目标大小
    numObjects = 0;
    for i = 1:cc.NumObjects
        if numel(cc.PixelIdxList{i}) > minObjectSize
            numObjects = numObjects + 1;
        end
    end
end

