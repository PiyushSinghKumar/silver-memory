getwd()
setwd('C:/Users/garim/Desktop/College/block3/product recommendation')


data <- read.csv("events.csv", header=T) 
summary(data) 
sum(is.na(data$event)) 
data <- data[!is.na(data$event),] 
A <- round(0.01*length(data$event)) 
sampledata <- data[sample(nrow(data), A[1]),]
summary(sampledata)
likesdata <- subset(sampledata,data$event=="addtocart",)
viewsdata <- subset(sampledata,data$event=="view",)
write.csv(likesdata,"likes.csv")
write.csv(viewsdata,"views.csv")
