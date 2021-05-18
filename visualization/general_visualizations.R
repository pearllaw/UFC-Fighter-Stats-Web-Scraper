# Import libraries
library(dplyr)
library(ggplot2)
library(lubridate)
library(ggrepel)

########## Visualizations from cleaned data in fighters2 data frame ############

# Find unique rows for fighters & weight classes they have belonged to in the past
gender_weight <- fighters2 %>%
  distinct(Name, `Weight Class`, Gender)

### Bar chart to show cross classification counts by weight class and gender
ggplot(gender_weight) + 
  geom_bar(
    aes(y = `Weight Class`, fill = Gender), 
    position = "dodge", 
    width = 0.8
  ) + 
  ggtitle("Number of UFC Fighters in each Weight Class by Gender") +
  xlab("Count") +
  theme(plot.title = element_text(hjust = 0.5))

# Mean & SD for each weight class and gender: height, reach
height_reach <- fighters2 %>%
  distinct(Name, `Weight Class`, Gender, Height_cm, Reach) %>%
  group_by(`Weight Class`, Gender) 

### Box plot showing fighter heights (cm) by weight class & gender with jitter to show 
### distribution behind each group & mean value 
ggplot(height_reach, aes(x = `Weight Class`, y = Height_cm, color = Gender)) +
  geom_boxplot(outlier.shape=NA, position = position_dodge(width = 1.25)) +
  geom_point(position = position_jitterdodge(jitter.width = 0.15, dodge.width = 1.25), 
             alpha = 0.4, size = 2.5) +
  stat_summary(aes(group = Gender), fun = mean, geom = "point", 
               position = position_dodge(1.25), shape = 18, size = 3, color = "black") +
  facet_wrap(~`Weight Class`, scale = "free_x") +
  ggtitle("UFC Fighter Heights by Weight Class and Gender") +
  xlab("") +
  ylab("Height (cm)") +
  theme(plot.title = element_text(hjust = 0.5),
        axis.text.x = element_blank(),
        axis.ticks.x = element_blank())

### Box plot showing fighter reach (in) by weight class & gender with jitter to show 
### distribution behind each group & mean value 
ggplot(height_reach, aes(x = `Weight Class`, y = Reach, color = Gender)) +
  geom_boxplot(outlier.shape=NA, position = position_dodge(width = 1.25)) + 
  geom_point(position = position_jitterdodge(jitter.width = 0.15, dodge.width = 1.25), 
             alpha = 0.4, size = 2.5) +
  stat_summary(aes(group = Gender), fun = mean, geom = "point", 
               position = position_dodge(1.25), shape = 18, size = 3, color = "black") +
  facet_wrap(~`Weight Class`, scales = "free_x") +
  ggtitle("UFC Fighter Reach by Weight Class and Gender") + 
  xlab("") +
  ylab("Reach (in)") +
  theme(plot.title = element_text(hjust = 0.5),
        axis.text.x = element_blank(),
        axis.ticks.x = element_blank())

# Number of fighters for each stance 
stance_summary <- fighters2 %>%
  distinct(Name, Stance) %>%
  group_by(Stance) %>%
  summarize(Count = n())

### Bar chart showing proportion of stances for all fighters
ggplot(stance_summary) +
  geom_col(aes(x = Count, y = Stance, fill = Stance)) + 
  ggtitle("Number of Fighters per Stance") + 
  theme(plot.title = element_text(hjust = 0.5))