# Load libraries
library(tidyverse)
library(readr)
library(lubridate)

# Import data from csv files
fighters <- read_csv("fighter_stats_events_05-05-2021.csv")
events <- read_csv("ufc_events_05-07-2021.csv")

############################# Clean events data #################################
# Pivot F1, F2 columns into one column and remove duplicate rows 
pvt_events <- events %>%
  pivot_longer(cols=c("F1", "F2"), names_to="F1/2", values_to="Fighter") 

# Add new column "Gender" for fighter's gender, assign based off Weight_Class
events2 <- pvt_events %>%
  select(-"F1/2") %>%
  mutate(Gender = ifelse(str_detect(Weight_Class, "Women"), "F", "M")) 

# Remove all "Women's" substring out of Weight_Class column 
events2$Weight_Class <- gsub("Women's ", "", events2$Weight_Class)

# Remove duplicate rows 
events3 <- distinct(events2)

############################ Clean fighters data ################################
# Replace "--" and "" values with NA
fighters <- fighters %>% 
  mutate_all(na_if, "--") %>%
  mutate_all(na_if, "")

# Replace values in W/L column
fighters <- fighters %>%
  mutate("W/L" = ifelse(str_detect(`W/L`, "win"), "W", "L"))

# Reformat column values
fighters$Height <- gsub('"', "", fighters$Height)
fighters$Weight <- gsub(" lbs.", "", fighters$Weight)
fighters$Reach <- gsub('[-"]', "", fighters$Reach)
fighters$Str_Acc <- gsub("%", "", fighters$Str_Acc)
fighters$Str_Def <- gsub("%", "", fighters$Str_Def)
fighters$TD_Acc <- gsub("%", "", fighters$TD_Acc)
fighters$TD_Def <- gsub("%", "", fighters$TD_Def)

# Convert Height units (ft/in) into (cm)
fighters <- fighters %>% 
  separate(Height, into = c("Feet", "Inches"), "'", convert = TRUE) 
# Use add_column instead of mutate to place new Cm column right after Inches column
fighters <- fighters %>%
  mutate(`Height_cm` = (12*Feet + Inches)*2.54, .keep = "unused", .after = "Inches")

# Convert DOB & Date column from character to Date type
fighters$DOB <- as.Date(fighters$DOB, "%b %d, %Y")
fighters$Date <- as.Date(fighters$Date, "%b. %d, %Y")

# Convert certain columns from char to numeric type
to_num <- c("Weight", "Reach", "Str_Acc", "Str_Def", "TD_Acc", "TD_Def", "KD", 
            "Opp_KD", "Str", "Opp_Str", "TD", "Opp_TD", "Sub", "Opp_Sub")
fighters[to_num] <- sapply(fighters[to_num], as.numeric)

# Calculate and insert Age (today - DOB) and Fight Age (Date - DOB) columns
fighters <- fighters %>% 
  mutate(Age = as.numeric(Sys.Date() - DOB) %/% 365.25, .after = Name) %>%
  mutate(`Fight Age` = as.numeric(Date - DOB) %/% 365.25, .keep = "unused", .after = Event)

# Rename columns
fighters <- fighters %>%
  rename(`Str Acc %` = Str_Acc,
        `Str Def %` = Str_Def,
        `TD Acc %` = TD_Acc,
        `TD Def %` = TD_Def,
        `TD Avg` = TD_Avg,
        `Sub Avg` = Sub_Avg,
        `Opp KD` = Opp_KD,
        `Opp Str` = Opp_Str,
        `Opp TD` = Opp_TD,
        `Opp Sub` = Opp_Sub)

################ Merge fighters & events data frames into single data frame ##############
fighters_merged <- merge(fighters, events3, by.x = c("Name", "Event"), by.y = c("Fighter", "Event"), all.x = TRUE)

# Change column order and exclude DOB column
fighters_merged <- fighters_merged %>%
  relocate(c("Gender", "Weight_Class"), .after = Age) %>%
  relocate("Event", .before = `Fight Age`) 

# Keep only rows where specified columns are not NA and have a value
fighters2 <- fighters_merged %>%
  drop_na(Gender, Weight_Class, Event, KD, `Opp KD`, Str, `Opp Str`, TD, `Opp TD`, Sub, `Opp Sub`) 

# Get all events organized through UFC  
fighters2 <- fighters2 %>%
  filter(grepl("UFC|Ultimate Fighter", Event)) %>%
  rename(`Weight Class` = Weight_Class)



