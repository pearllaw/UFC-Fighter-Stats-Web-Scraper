# Import libraries
library(dplyr)
library(ggplot2)
library(lubridate)
library(ggrepel)

########## Visualizations from cleaned data in fighters2 data frame ############

# Individual Athlete Stat analysis (sub fighter variable with value from Name column) 
fighter <- "Rose Namajunas"
fighter_df <- fighters2[fighters2$Name == fighter, ]

# Calculate fighter & opponent KD, Str, TD, Sub percentages
KD_sum <- apply(fighter_df[, 25:26], 1, sum)
Str_sum <- apply(fighter_df[, 27:28], 1, sum)
TD_sum <- apply(fighter_df[, 29:30], 1, sum)
Sub_sum <- apply(fighter_df[, 31:32], 1, sum)
fighter_df <- fighter_df %>%
  mutate(`KD %` = ifelse(!fighter_df$KD, 0, fighter_df$KD / KD_sum * 100),
         `Opp KD %` = ifelse(!fighter_df$`Opp KD`, 0, fighter_df$`Opp KD` / KD_sum *100),
         `Str %` = ifelse(!fighter_df$Str, 0, fighter_df$Str / Str_sum * 100), 
         `Opp Str %` = ifelse(!fighter_df$`Opp Str`, 0, fighter_df$`Opp Str` / Str_sum * 100),
         `TD %` = ifelse(!fighter_df$TD, 0, fighter_df$TD / TD_sum * 100),
         `Opp TD %` = ifelse(!fighter_df$`Opp TD`, 0, fighter_df$`Opp TD` / TD_sum * 100),
         `Sub %` = ifelse(!fighter_df$Sub, 0, fighter_df$Sub / Sub_sum * 100),
         `Opp Sub %` = ifelse(!fighter_df$`Opp Sub`, 0, fighter_df$`Opp Sub` / Sub_sum * 100))

# Summarize mean stats based on W/L outcome, Weight Class(es), and Method
fighter_mean_stats <- fighter_df %>%
  group_by(`W/L`, `Weight Class`, Method) %>%
  summarise(
    `KD` = mean(`KD %`),
    `STR` = mean(`Str %`),
    `TD` = mean(`TD %`),
    `SUB` = mean(`Sub %`)
  )

# Pivot data longer
fighter_mean_stats <- fighter_mean_stats %>% 
  pivot_longer(cols = 4:7, names_to = "Statistic", values_to = "value") 

### Bar chart to show fighter summary stats
ggplot(fighter_mean_stats) +
  geom_col(aes(x = reorder(`W/L`, desc(`W/L`)), y = value, fill = Statistic), position = "dodge") +
  facet_grid(`Weight Class` ~ Method, scales = "free") + 
  scale_x_discrete(labels = c("Win", "Loss")) +
  labs(title = "Average Percent of Individual Fight Statistic for Fights Won and Lost by Method and Weight Class", 
       caption = "KO/TKO: (Technical)/Knockout, U-DEC: Unanimous decision, KD: Knockdowns, STR: Significant Strikes, SUB: Submission Attempts, TD: Takedowns") +
  xlab("") +
  ylab("Percent") +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  theme(plot.title = element_text(hjust = 0.5),
        plot.caption = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") 

# Summarize fighter's avg finish round & time
finish_round_time <- fighter_df %>%
  group_by(`W/L`, `Weight Class`, Method) %>%
  summarise(
    `Fight count` = n(),
    `Avg finish round` = mean(Round),
  )

### Bar chart showing average finish round 
ggplot(finish_round_time, aes(x = reorder(`W/L`, desc(`W/L`)), y = `Avg finish round`, fill = Method)) +
  geom_col(position = "dodge") +
  geom_text(aes(label = paste0("n = ", `Fight count`)), 
            position = position_dodge(0.9), vjust = 0, size = 3) +
  facet_wrap(~`Weight Class`, scales = "free") + 
  scale_x_discrete(labels = c("Win", "Loss")) +
  labs(title = "Average Number of Rounds Fought by Method and Weight Class", 
       caption = "KO/TKO: (Technical)/Knockout, SUB: Submission, U-DEC: Unanimous decision") +
  xlab(c(0, 45)) +
  ylab("Rounds") +
  theme(plot.title = element_text(hjust = 0.5),
        plot.caption = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") 

# Comparing fight age (experience factor) to W/L outcome 
age_win_loss <- fighter_df %>%
  group_by(`Fight Age`, `Weight Class`, `W/L`) %>%
  summarise(
    Count = n()
  )

### Stacked bar chart comparing win/lose ratio in each weight class to age 
ggplot(age_win_loss) +
  geom_col(aes(x = `Fight Age`, y = Count, fill = `W/L`)) +
  facet_wrap(~`Weight Class`) +
  ggtitle("Win-lose Fight Ratio by Weight Class and Age") + 
  xlab("Age") +
  ylab("Total Fights") +
  theme(plot.title = element_text(hjust = 0.5))












