args = commandArgs(trailingOnly=TRUE)
library(tuneR, warn.conflicts = F, quietly = T) 

RMS <- function(num) {sqrt(sum(num^2)/length(num))}

# Assumes 12 channels (ie .wav files) in the fileRepo
extractMatrix <- function (fileRepo, intervalLen, verbose=FALSE, showWarnings=TRUE) {
  files <- list.files(path=fileRepo, pattern="*.wav", full.names=TRUE, recursive=TRUE, include.dirs = TRUE)
  
  # max <- 0
  # for (file in files){
  #   sound = readWave(file)
  #   length = length(sound)
  #   if(!is.null(length) && length > max){ max <- length }  }
  firstOne <- readWave(files[[1]])
  max <- length(firstOne) / firstOne@samp.rate 
  print(max)
  print(intervalLen)
  resLen <- max/intervalLen 

  mRes <- matrix(nrow = 12, ncol = resLen)
  rowCounter = 1
  
  for(fin in files){
    # read in audio file
    data = readWave(fin)
    
    # extract signal
    # length is 2,880,000
    snd = data@left

    factor <- length(snd)/resLen
    
    # cut down the amount of samples
    intervaledSnd = resLen
    for(i in 1:resLen){
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
    
    timeArray <- (1:resLen) * intervalLen
    #timeArray <- ((0:(length(intervaledSnd)-1))) / (data@samp.rate) * 60

    rowCounter = rowCounter + 1
    
  }
  
  
  rownames(mRes) <- c("Mic1", "Mic2", "Mic3", "Mic4","Mic5", "Mic6", "Mic7", "Mic8","Mic9", "Mic10","Mic11", "Mic12")
  colnames(mRes) <- timeArray
  
  mRes <- t(mRes)
  print(length(mRes))
  #colnames(mRes) <- c("Mic1", "Mic2", "Mic3", "Mic4","Mic5", "Mic6", "Mic7", "Mic8","Mic9", "Mic10","Mic11", "Mic12")
  #rownames(mRes) <- timeArray
  
  write.csv(mRes,file="data.csv")

}
  
# Collect csvFiles
extractMatrix(args[1], as.numeric(args[2]))