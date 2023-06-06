%Show a picture of the MOT and its reflection, with analysis
%results
if(1) %Any conditions for doing this analysis
    clear('MOTPosAnalysisResults','variable');




    % Gather Images
    % Gather Images
    % Gather Images
    
    img = imread(sprintf('\\\\YBCLOCK%s\\Photos\\%s_%04d_%02d.bmp',filenamerootfolder,fnameprefix,fnum,0));
    imgb = imread(sprintf('\\\\YBCLOCK%s\\Photos\\%s_%04d_%02d.bmp',filenamerootfolder,fnameprefix,fnum,1)); 
    



    %Removing background and creating a vector out of a Matrix.
    imgODDiff = reshape(log(double(img))-log(double(imgb)),1,[]);

    imgODDiffmean = mean(imgODDiff(imgODDiff>-2 & imgODDiff<2));


    
    imgd = double(img)-double(imgb)*exp(imgODDiffmean);
    ximage = 195:255;
    yimage.direct = 316:423;
    yimage.reflected = 223:315;
    
    imgddirect = imgd(ximage,yimage.direct);
    imgdreflected = imgd(ximage,yimage.reflected);
    
    % Extra processing for cropping out bits of direct image
    % that can pollute the reflected image.
    if(0)
        for imgrownum = 1:size(imgdreflected,1)
            for imgcolnum = 1:size(imgdreflected,2)
                if ( 71 < imgcolnum && imgcolnum < 77 && 11 < imgrownum && imgrownum < 15)
                    imgdreflected(imgrownum,imgcolnum) = 0;
                end
            end
        end   
    end

    map = jet(256);
    if(~exist('./AnalysisPlots/MOTImages','dir'))
        mkdir('./AnalysisPlots/MOTImages')
    end
    imwrite([imgddirect imgdreflected],map,sprintf('./AnalysisPlots/MOTImages/%s_%04d.png',fnameprefix,fnum));
    
    if(1) %More code folding, fitting Gaussians to the MOT images
    
        reduced = 1;
        
        x = ximage;
        z = sum(imgddirect,2)';
        if reduced
            mid = find(z==max(z),1);
            if mid>10 && mid<length(x)-10;
            x = x(mid-10:mid+10); z = z(mid-10:mid+10);
            end
        end
        zerr = ones(size(z));
        xeval = x;
        graph.flag = 0;
        graph.fname = sprintf('./AnalysisPlots/MOTImages/%s_%04d_xFit.png',fnameprefix,fnum);
        graph.xlabel = 'Position [px]';
        graph.ylabel = 'Brightness';
        graph.title = '';
        fitres = FitGaussianOffsErrBar (x,z,zerr,xeval,graph);

        MOTPosAnalysisResults.direct.x(:) = fitres;

        x = yimage.direct;
        z = sum(imgddirect,1);
        
        if reduced
            mid = find(z==max(z),1);
            if mid>10 && mid<length(x)-10;
            x = x(mid-10:mid+10); z = z(mid-10:mid+10);
            end
        end
        zerr = ones(size(z));
        xeval = x;
        %graph.flag = 1;
        graph.fname = sprintf('./AnalysisPlots/MOTImages/%s_%04d_yFit.png',fnameprefix,fnum);
        graph.xlabel = 'Position [px]';
        graph.ylabel = 'Brightness';
        graph.title = '';
        fitres = FitGaussianOffsErrBar (x,z,zerr,xeval,graph);

        MOTPosAnalysisResults.direct.y(:) = fitres;

        % Now the reflected image
        reduced=1
        x = ximage;
        z = sum(imgdreflected,2)';
        if reduced
            mid = round(MOTPosAnalysisResults.direct.x(1));
            if mid>10 && mid<length(x)-10;
            x = x(mid-10:mid+10); z = z(mid-10:mid+10);
            end
        end
        zerr = ones(size(z));
        xeval = x;
        %graph.flag = 1;
        graph.fname = sprintf('./AnalysisPlots/MOTImages/%s_%04d_xReflFit.png',fnameprefix,fnum);
        graph.xlabel = 'Position [px]';
        graph.ylabel = 'Brightness';
        graph.title = '';
        fitres = FitGaussianOffsErrBar (x,z,zerr,xeval,graph);

        MOTPosAnalysisResults.reflected.x(:) = fitres;

        x = yimage.reflected;
        z = sum(imgdreflected,1);
        if reduced
            mid = yimage.direct(1)-round(MOTPosAnalysisResults.direct.y(1)-yimage.direct(1)+1);
            if mid>10 && mid<length(x)-10;
            x = x(mid-10:mid+10); z = z(mid-10:mid+10);
            end
        end
        zerr = ones(size(z));
        xeval = x;
        %graph.flag = 1;
        graph.fname = sprintf('./AnalysisPlots/MOTImages/%s_%04d_yReflFit.png',fnameprefix,fnum);
        graph.xlabel = 'Position [px]';
        graph.ylabel = 'Brightness';
        graph.title = '';
        fitres = FitGaussianOffsErrBar (x,z,zerr,xeval,graph);

        MOTPosAnalysisResults.reflected.y(:) = fitres;  
    end                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
    
    MOTPosAnalysisResults.x.val=MOTPosAnalysisResults.direct.x(1)*1.36*12.32e-3;
    MOTPosAnalysisResults.x.err=MOTPosAnalysisResults.direct.x(5)*1.36*12.32e-3;
    MOTPosAnalysisResults.y.val=MOTPosAnalysisResults.direct.y(1)*1.36*12.32e-3;
    MOTPosAnalysisResults.y.err=MOTPosAnalysisResults.direct.y(5)*1.36*12.32e-3;
    MOTPosAnalysisResults.dist.val = (1.36*12.32e-3/cos(15.16*pi/180))*(MOTPosAnalysisResults.direct.y(1)-MOTPosAnalysisResults.reflected.y(1))/2;
    MOTPosAnalysisResults.dist.err = (1.36*12.32e-3/cos(15.16*pi/180))*(MOTPosAnalysisResults.direct.y(5).^2+MOTPosAnalysisResults.reflected.y(5).^2)/2;
    width = MOTPosAnalysisResults.direct.x(:,2);
    widtherr = MOTPosAnalysisResults.direct.x(:,6);
    peakht = MOTPosAnalysisResults.direct.x(:,3);
    peakhterr = MOTPosAnalysisResults.direct.x(:,7);
    MOTPosAnalysisResults.brightness.val = width.*peakht;
    MOTPosAnalysisResults.brightness.err = widtherr.*peakht+width.*peakhterr;
    
    
    %imagesc(maxt*[0.2 0.4],maxval*[0.9 1.1],imgddirect,[0 200]);
    image(maxt*[0.0 0.4],maxval*[0.9 1.1],ind2rgb(round([imgdreflected imgddirect]),hot(200)));
    
    colormap('hot');
    
    text(maxt*0.45,maxval*1.05,sprintf('x_{MOT}=%.3f\\pm%.3f mm',MOTPosAnalysisResults.x.val,MOTPosAnalysisResults.x.err),'FontSize',12);
    text(maxt*0.45,maxval*1.0,sprintf('y_{MOT}=%.3f\\pm%.3f mm',MOTPosAnalysisResults.y.val,MOTPosAnalysisResults.y.err),'FontSize',12);
    
    text(maxt*0.45,maxval*0.95,sprintf('z_{MOT}=%.3f\\pm%.3f mm',MOTPosAnalysisResults.dist.val,MOTPosAnalysisResults.dist.err),'FontSize',12);
    text(maxt*0.45,maxval*0.9,sprintf('I_{MOT}=%.3f\\pm%.3f',1e-3*MOTPosAnalysisResults.brightness.val,1e-3*MOTPosAnalysisResults.brightness.err),'FontSize',12);
    
    logfilewrite('log.txt',sprintf('MOT Position Fit Results:\n'));
    logfilewrite('log.txt',sprintf('x \t y \t Distance \t Intensity \t dx \t dy \t dDistance \t dIntensity \n'));
    fieldnames = {'x','y','dist','brightness'};
    MOTPosRes = zeros([1 2*length(fieldnames)]);
    for i = 1:length(fieldnames)
        fieldname = fieldnames{i};
        MOTPosRes(i) = MOTPosAnalysisResults.(fieldname).val;
        MOTPosRes(i+length(fieldnames)) = MOTPosAnalysisResults.(fieldname).err;
    end
    logfilewrite('log.txt',sprintf('%.6f\t',MOTPosRes));
    logfilewrite('log.txt',sprintf('\n'));
    logfilewrite(fnamefitsave,sprintf('%.6f\t',MOTPosRes));
    
end

xlabel('Time [s]')
ylabel(sprintf('Photons in %.2fms',binlengthrawplot/1e6))
title(fname,'Interpreter','none','FontSize',12);
hold off
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%