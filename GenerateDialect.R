library(jsonlite)

#setwd('Models/AAE')
printf <- function(...) invisible(cat(sprintf(...)))

# LOAD AND FORMAT DATA
jdat <- fromJSON('stimopts.json')
tmp <- read.delim(jdat$phon_map, header=F,sep = ' ', strip.white=T)
labs <- tmp[,1]
d <- as.data.frame(t(tmp[,2:ncol(tmp)]))
names(d) <- labs
rownames(d) <- NULL
d <- d[1:25,]

m <- as.matrix(d)
m <- t(m)

# CATEGORIZE SYMBOLS
vowels = c(
  'A','a','@', #'&',
  'c',
  'E','e','I','i',
  'O','o',
  'U','u','^',
  'W', #'w',
  'Y'
)
consonants = c(
  'd',
  'f', #'F',
  'G','g',
  'H','h',
  'J','j',
  'K','k',
  'L','l',
  'M','m',
  'N','n',
  'P','p',
  'Q','q',
  'R','r',
  's','t',
  'V','v',
  'x',
  'z'
)
th = c('T','D')
fricatives = c('T','D','C','S','Z')

# GENERATE DIALECT

# Only vowels are distorted. 'w' is skipped, since it patterns more like the
# consonants (note that it is removed from the vowels, above. The @ is not
# actually implemented, so that is removed, too). There is one unit that is
# originally active for all vowels---this unit is left as is. There is one unit
# that is never used for the vowels, after removing 'w'. This is also left
# alone.

# 'a' and 'W' cannot be modified without sounding more like another vowel than
# the original. These are ultimately left as-is.

# The distribution of active units is skewed in the original reps. That is,
# there are more with 2 active units than 3 active units, etc. See below:
#hist(rowSums(m[vowels,vcols]))

# The procedure approximates this distribution, but does not guarantee that
# dialectic changes involve the same number of active units as the original.

vcols <- c(14,15,16,17,18,19,20,22,23,24)
m_d <- m
maxiter <- 10000
stayedsame <- NULL
m_log <- matrix(0,nrow=length(vowels),ncol=length(vcols))
rownames(m_log) <- vowels
for (v in vowels) {
  printf('%s:      ', v)
  x <- m[v,vcols]
  y <- m[vowels, vcols]
  y <- y[!(vowels %in% v),]
  iter = 0
  while (TRUE) {
    n <- sample(c(2,2,2,3,3,4,5),1)
    z <- rep(0,length(x))
    z[1:n] <- 1
    z <- sample(z)
    if (all(z == x)) { next }
    dzx <- dist(rbind(z,x),method='manhattan')
    dzy <- dist(rbind(z,y),method='manhattan')[1:14]
    if ((iter %% 100)==0) {
      printf('\b\b\b\b\b% 5d',iter)
    }
    newz <- TRUE
    for (i in 1:length(vowels)) {
      oldz <- m_log[i,]
      if (all(oldz==z)) {
        newz <- FALSE
        break
      }
    }
    if (all(dzx<dzy) & newz) {
      m_log[v,] <- z
      m_d[v,vcols] <- z
      printf('\b\b\b\b\b% 5d\n',iter)
      break
    }
    if (iter >= maxiter) {
      m_d[v,vcols] <- x
      stayedsame <- append(stayedsame,v)
      printf('\b\b\b\b\b% 5d\n',iter)
      break
    }
    iter <- iter + 1
  }
}
# write.table(m_d, "raw/mapping_dialect_weak",quote=FALSE, col.names=FALSE)
m_d <- read.table('raw/mapping_dialect',header=F)
head(m_d)
rownames(m_d) <- m_d[,1]
m_d <- m_d[,-1]
colnames(m_d) <- 1:ncol(m_d)

# CONSONANTS
ccols <- 1:13
uc <- consonants %in% rownames(m)
# m_d <- m
maxiter <- 10000
stayedsame <- NULL
m_log <- matrix(0,nrow=length(consonants[uc]),ncol=length(ccols))
rownames(m_log) <- consonants[uc]
for (cc in consonants[uc]) {
  printf('%s:      ', cc)
  x <- m[cc,ccols]
  y <- m[consonants[uc], ccols]
  y <- y[!(consonants[uc] %in% cc),]
  iter = 0
  while (TRUE) {
    n <- sample(c(2,2,2,3,3,4,5),1)
    z <- rep(0,length(x))
    z[1:n] <- 1
    z <- sample(z)
    if (all(z == x)) { next }
    dzx <- dist(rbind(z,x),method='manhattan')
    dzy <- dist(rbind(z,y),method='manhattan')[1:14]
    if ((iter %% 100)==0) {
      printf('\b\b\b\b\b% 5d',iter)
    }
    newz <- TRUE
    for (i in 1:length(consonants[uc])) {
      oldz <- m_log[i,]
      if (all(oldz==z)) {
        newz <- FALSE
        break
      }
    }
    if (all(dzx<dzy) & newz) {
      m_log[cc,] <- z
      m_d[cc,ccols] <- z
      printf('\b\b\b\b\b% 5d\n',iter)
      break
    }
    if (iter >= maxiter) {
      m_d[cc,ccols] <- x
      stayedsame <- append(stayedsame,cc)
      printf('\b\b\b\b\b% 5d\n',iter)
      break
    }
    iter <- iter + 1
  }
}

write.table(m_d, "raw/mapping_dialect_strong",quote=FALSE, col.names=FALSE)
