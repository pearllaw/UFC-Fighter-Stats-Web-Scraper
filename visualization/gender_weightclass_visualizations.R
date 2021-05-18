# Import libraries
library(dplyr)
library(ggplot2)
library(ggcorrplot)
################ Visualizations from gender_weightclass_df.R ##################

df.list <- list(m_bantamweight, m_catchweight, m_featherweight, m_flyweight, 
                m_heavyweight, m_light_heavyweight, m_lightweight, m_middleweight, 
                m_welterweight, f_bantamweight, f_featherweight, f_flyweight, f_strawweight)
loop.vector <- c(9, 11, 13:20)

data <- lapply(df.list, function(x) subset(x, select = loop.vector))

for (d in data) {
  corr <- round(cor(d, use = "complete.obs"), 1)
  p <- ggcorrplot(corr, p.mat = cor_pmat(d), sig.level = 0.01, insig = "blank", 
                  hc.order = TRUE, type = "lower", lab = TRUE) 
  print(p)
}

