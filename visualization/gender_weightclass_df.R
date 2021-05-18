# Import libraries
library(dplyr)

################# Male fighters & respective weight classes ####################
m_welterweight <- fighters2 %>%
  filter(Gender == "M", `Weight Class` == "Welterweight") %>%
  distinct(Name, .keep_all = TRUE) 

m_super_heavyweight <- fighters2 %>%
  filter(Gender == "M", `Weight Class` == "Super Heavyweight") %>%
  distinct(Name, .keep_all = TRUE) 

m_openweight <- fighters2 %>%
  filter(Gender == "M", `Weight Class` == "Open Weight") %>%
  distinct(Name, .keep_all = TRUE) 

m_middleweight <- fighters2 %>%
  filter(Gender == "M", `Weight Class` == "Middleweight") %>%
  distinct(Name, .keep_all = TRUE) 

m_lightweight <- fighters2 %>%
  filter(Gender == "M", `Weight Class` == "Lightweight") %>%
  distinct(Name, .keep_all = TRUE) 

m_light_heavyweight <- fighters2 %>%
  filter(Gender == "M", `Weight Class` == "Light Heavyweight") %>%
  distinct(Name, .keep_all = TRUE) 

m_heavyweight <- fighters2 %>%
  filter(Gender == "M", `Weight Class` == "Heavyweight") %>%
  distinct(Name, .keep_all = TRUE) 

m_flyweight <- fighters2 %>%
  filter(Gender == "M", `Weight Class` == "Flyweight") %>%
  distinct(Name, .keep_all = TRUE) 

m_featherweight <- fighters2 %>%
  filter(Gender == "M", `Weight Class` == "Featherweight") %>%
  distinct(Name, .keep_all = TRUE) 

m_catchweight <- fighters2 %>%
  filter(Gender == "M", `Weight Class` == "Catch Weight") %>%
  distinct(Name, .keep_all = TRUE) 

m_bantamweight <- fighters2 %>%
  filter(Gender == "M", `Weight Class` == "Bantamweight") %>%
  distinct(Name, .keep_all = TRUE) 

################# Female fighters & respective weight classes ####################
f_strawweight <- fighters2 %>%
  filter(Gender == "F", `Weight Class` == "Strawweight") %>%
  distinct(Name, .keep_all = TRUE) 

f_flyweight <- fighters2 %>%
  filter(Gender == "F", `Weight Class` == "Flyweight") %>%
  distinct(Name, .keep_all = TRUE) 

f_featherweight <- fighters2 %>%
  filter(Gender == "F", `Weight Class` == "Featherweight") %>%
  distinct(Name, .keep_all = TRUE) 

f_bantamweight <- fighters2 %>%
  filter(Gender == "F", `Weight Class` == "Bantamweight") %>%
  distinct(Name, .keep_all = TRUE) 
