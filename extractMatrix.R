args = commandArgs(trailingOnly=TRUE)
library(tuneR, ggplot2, warn.conflicts = F, quietly = T) 

RMS <- function(num) {sqrt(sum(num^2)/length(num))}

# Assumes 12 channels (ie .wav files) in the fileRepo
extractMatrix <- function (fileRepo, verbose=FALSE, showWarnings=TRUE) {
  files <- list.files(path=fileRepo, pattern="*.wav", full.names=TRUE, recursive=TRUE, include.dirs = TRUE)
  
  max <- 0
  for (file in files){
    sound = readWave(file)
    length = length(sound)
    if(!is.null(length) && length > max){ max <- length }  }
  
  mRes <- matrix(nrow = 12, ncol = 1200)
  rowCounter = 1
  
  for(fin in files){
    # read in audio file
    data = readWave(fin)
    
    # extract signal
    # length is 2,880,000
    snd = data@left

    factor <- length(snd)/1200
    
    # cut down the amount of samples
    intervaledSnd = 1200
    for(i in 1:1200){
      end = 0
      if(factor*(i+1) > length(snd)){end = length(snd)-1}else{end = factor*(i+1)}
      range <- snd[(factor*i) : end]
      # print("now considering the subvectors from ")
      # print(factor*i)
      # print("to")
      # print(end)
      intervaledSnd[[i]] <- RMS(range)
      #print(intervaledSnd[[i]])
    }

    # print(snd)
    mRes[rowCounter, ] <- intervaledSnd
    
    timeArray <- (0:1200)
    #timeArray <- ((0:(length(intervaledSnd)-1))) / (data@samp.rate) * 60

    rowCounter = rowCounter + 1
    
  }
  
  
  
  mRes <- t(mRes)
  print(length(mRes))
  #colnames(mRes) <- c("Mic1", "Mic2", "Mic3", "Mic4","Mic5", "Mic6", "Mic7", "Mic8","Mic9", "Mic10","Mic11", "Mic12")
  #rownames(mRes) <- timeArray
  
  write.csv(mRes,file="data.csv")

}


# This function finds the longest duration given a list of (wav) files.
findMaxDuration <- function(fileList, verbose=FALSE, showWarnings=TRUE) {
  
}
  
# Collect csvFiles
extractMatrix(args[1])