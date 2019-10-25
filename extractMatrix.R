args = commandArgs(trailingOnly=TRUE)
library(tuneR, warn.conflicts = F, quietly = T) 

RMS <- function(num) {sqrt(sum(num^2)/length(num))}

# Assumes 12 channels (ie .wav files) in the fileRepo
extractMatrix <- function (fileRepo, intervalLen, verbose=FALSE, showWarnings=TRUE) {
  files <- list.files(path=fileRepo, pattern="*.wav", full.names=TRUE, recursive=TRUE, include.dirs = TRUE)
  
  # Figure out duration & calculate length of the resultin gmatrix based on the interval length
  firstOne <- readWave(files[[1]])
  max <- length(firstOne) / firstOne@samp.rate 
  resLen <- max/intervalLen
  print(max)
  print(intervalLen)
  print(resLen) 

  mRes <- matrix(nrow = 12, ncol = resLen)
  rowCounter = 1
  
  for(fin in files){
    # read in audio file
    data = readWave(fin)
    
    # extract signal # length is 2,880,000
    snd = data@left

    # take RMS over an interval
    factor <- length(snd)/resLen
    intervaledSnd = resLen
    for(i in 1:resLen){
      end = 0
      if(factor*(i+1) > length(snd)){end = length(snd)-1}else{end = factor*(i+1)}
      range <- snd[(factor*i) : end]
      intervaledSnd[[i]] <- RMS(range)
    }

    # print(snd)
    mRes[rowCounter, ] <- intervaledSnd
    
    rowCounter = rowCounter + 1
    
  }
  
  # add labels to the matrix
  rownames(mRes) <- c("Mic1", "Mic2", "Mic3", "Mic4","Mic5", "Mic6", "Mic7", "Mic8","Mic9", "Mic10","Mic11", "Mic12")
  colnames(mRes) <- (1:resLen) * intervalLen
  print((1:resLen)*intervalLen)
  
  # transpose & output
  mRes <- t(mRes)
  write.csv(mRes,file="data.csv")

  print("Finished.")
}
  
if(length(args) < 2) {print("Please input an interval length (as a arabic number).")}
extractMatrix(args[1], as.numeric(args[2]))