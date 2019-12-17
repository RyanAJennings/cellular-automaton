num_agents = c(45, 90, 135, 180, 225, 270, 315, 360, 405, 495, 540, 585, 630)
resource_prob = c(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
field_of_vision = c(1, 2, 3, 4, 5)
metabolic_rate = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

plotAnalysis = function(filename, values, x_label, title) {
  filename = paste("output/", filename, ".txt", sep="")
  data = scan(filename)
  averages = c()
  mostWins = c()
  standardDeviations = c()
  for (i in 1:length(values)) {
    win_counts = data[((i-1)*21 + 1) : (i*21)]
    sum = 0
    wins = c()
    for (j in 1:21) {
      sum = sum + win_counts[j] * (j-11)
      for (k in 1:win_counts[j]) {
        wins = c(wins, j-11)
      }
    }
    standardDeviations = c(standardDeviations, sd(wins))
    averages = c(averages, sum / 100)
    mostWins = c(mostWins, mean(which(win_counts == max(win_counts)))-11)
  }
  print(averages)
  print(mostWins)
  print(standardDeviations)
  par(mfrow = c(1, 3))
  plot(values, averages, xlim = c(min(values),max(values)), ylim = c(-10,10),
       bty = "n", xlab = x_label, ylab = "Winning strategy average", las = 1,
       main = paste("Average winning strategy vs", title))
  
  plot(values, mostWins, xlim = c(min(values),max(values)), ylim = c(min(mostWins),max(mostWins)),
       bty = "n", xlab = x_label, ylab = "Most winning strategy", las = 1,
       main = paste("Most winning strategy vs", title))
  
  plot(values, standardDeviations, xlim = c(min(values),max(values)), ylim = c(min(standardDeviations),max(standardDeviations)),
       bty = "n", xlab = x_label, ylab = "Standard deviation in winning strategy", las = 1,
       main = paste("Standard deviation vs", title))
  
}

plotAnalysis("num_agents", num_agents, "Number of agents in the simulation", "number of agents")
plotAnalysis("resource_prob", resource_prob, "Probability for a resource cell", "resource probability")
plotAnalysis("field_of_vision", field_of_vision, "Field of vision of each agent", "field of vision")
plotAnalysis("metabolic_rate", metabolic_rate, "Metabolic rate of each agent", "metabolic rate")

