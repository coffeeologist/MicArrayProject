args = commandArgs(trailingOnly=TRUE)
library(tuneR, ggplot2, warn.conflicts = F, quietly = T) 

# Assumes 12 channels (ie .wav files) in the fileRepo
extractMatrix <- function (fileRepo, verbose=FALSE, showWarnings=TRUE) {
  files <- list.files(path=fileRepo, pattern="*.wav", full.names=TRUE, recursive=TRUE, include.dirs = TRUE)
  
  max <- 0
  for (file in files){
    sound = readWave(file)
    length = length(sound)
    if(!is.null(length) && length > max){ max <- length }  }
  
  mRes <- matrix(nrow = 12, ncol = max)
  rowCounter = 1
  
  for(fin in files){
    # read in audio file
    data = readWave(fin)
    
    # extract signal
    snd = data@left

    #print(snd)
    mRes[rowCounter, ] <- snd
    
    timeArray <- ((0:(length(data)-1))) / data@samp.rate
    
    rowCounter = rowCounter + 1
    
  }
  
  
  
  mRes <- t(mRes)
  colnames(mRes) <- c("Mic1", "Mic2", "Mic3", "Mic4","Mic5", "Mic6", "Mic7", "Mic8","Mic9", "Mic10","Mic11", "Mic12")
  rownames(mRes) <- timeArray
  
  write.csv(mRes,file="data.csv")

}


# This function finds the longest duration given a list of (wav) files.
findMaxDuration <- function(fileList, verbose=FALSE, showWarnings=TRUE) {
  
}
  
# Collect csvFiles
extractMatrix(args[1])