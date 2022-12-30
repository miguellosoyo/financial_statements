# Importar librerías de trabajo
library(dplyr)
library(ggplot2)
library(ggthemes)

# Definir directorio de trabajo
# setwd('../Campaña de Marketing/bank-additional/bank-additional')

# Cargar información de la campaña de marketing
df <- read.csv('bank-additional-full.csv', sep=';', header=T)

# Calcular Tasa de Conversión ---- 

# Categorizar variable y
df <- df %>% 
  mutate(y=ifelse(y=='no', 0, 1))
df$y <- as.integer(df$y)

# Calcular el total de conversiones y total de clientes
conversions <- sum(df$y)
customers <- nrow(df)

# Obtener la tasa de conversión
conversion_rate <- round((conversions/customers)*100, 2)

# Analizar Conversión por Grupos de Edad ----

# Definir 7 grupos de edad (Teens (17-19), 20-30, 30-40, 40-50, 50-60, 60-70 y +70)
conversionAgeGroups <- df %>% group_by(AgeGroup=cut(age, breaks=append((17), seq(20, 70, by=10)))) %>%
  summarize(TotalCount=n(), NumberConversions=sum(y)) %>%
  mutate(ConversionRate=round(NumberConversions/TotalCount, 2)*100)

# Renombrar nombres del primer y último grupo
conversionAgeGroups$AgeGroup <- as.character(conversionAgeGroups$AgeGroup)
conversionAgeGroups$AgeGroup[1] <- 'Teens'
conversionAgeGroups$AgeGroup[7] <- '+70'

# Convertir a variables categóricas los grupos de edad
conversionAgeGroups$AgeGroup <- as.factor(conversionAgeGroups$AgeGroup)

# Crear un gráfico de dispersión para revisar las relaciones entre la tasa de conversión y los grupos de edad
ggplot(conversionAgeGroups, aes(x=AgeGroup, y=ConversionRate)) + 
  geom_point(aes(size=TotalCount)) + 
  xlab('Grupos de Edad') + 
  ylab('Tasa de Conversión') +
  labs(title='Tasa de Conversión por Grupos de Edad', size='Conteo de\nClientes')

# Analizar Conversión por Grupos de Edad y Estado Civil ----

# Obtener los grupos por edad y estado civil
conversionAgeMarital <- df %>%
  filter(y==1) %>%
  group_by(AgeGroup=cut(age, append((17), seq(20, 70, by=10))), 
           Marital=marital) %>%
  summarize(Count=n(), NumConversions=sum(y)) %>%
  mutate(TotalCount=sum(Count)) %>%
  mutate(ConversionRate=round((NumConversions/TotalCount)*100, 2))

# Integrar etiquedas Teens y +70
conversionAgeMarital$AgeGroup <- as.character(conversionAgeMarital$AgeGroup)
conversionAgeMarital$AgeGroup[is.na(conversionAgeMarital$AgeGroup)] <- '+70'
conversionAgeMarital$AgeGroup[conversionAgeMarital$AgeGroup=='(17,20]'] <- 'Teens'

# Crear un gráfico de barras para comparar las proporciones de estado civil para cada grupo
ggplot(conversionAgeMarital, aes(x=AgeGroup, y=ConversionRate, fill=Marital)) +
  geom_bar(width=0.5, stat='identity') + 
  xlab('Grupos de Edad') + 
  ylab('Tasa de Conversión') +
  labs(title='Tasa de Conversión por Grupos de Edad y Estado Civil', fill='Estado Civil') +
  scale_fill_discrete(labels=c('Divorciado', 'Casado', 'Soltero', 'Sin Definir'))
