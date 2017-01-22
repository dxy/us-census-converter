#!/usr/bin/python

"""Parse Population Projection data files released by US Census Bureau.

Aggregate age and sex since we're interested in ratio of each race out of the
total population (regardless of age).
"""

import argparse
import csv

class PopulationProjection(object):
  def __init__(self):
    self.white = {
        'hispanic': 0,
        'non_hispanic': 0,
    }
    self.black = {
        'hispanic': 0,
        'non_hispanic': 0,
    }
    self.indian_eskimo_aleut = {
        'hispanic': 0,
        'non_hispanic': 0,
    }
    self.asian_pacific = {
        'hispanic': 0,
        'non_hispanic': 0,
    }

  def __str__(self):
    return '%d %d %d %d %d %d %d %d' % (
        self.white['non_hispanic'], self.white['hispanic'],
        self.black['non_hispanic'], self.black['hispanic'],
        self.indian_eskimo_aleut['non_hispanic'],
        self.indian_eskimo_aleut['hispanic'],
        self.asian_pacific['non_hispanic'],
        self.asian_pacific['hispanic'])

  def GetAsList(self):
    return [
        self.white['non_hispanic'], self.white['hispanic'],
        self.black['non_hispanic'], self.black['hispanic'],
        self.indian_eskimo_aleut['non_hispanic'],
        self.indian_eskimo_aleut['hispanic'],
        self.asian_pacific['non_hispanic'],
        self.asian_pacific['hispanic']
    ]

"""Parse each line and write it to a proper CSV file.
"""
def UnusedParse(line, series_a_writer, series_b_writer):
  metadata = line[:9]
  data = line[9:]

  unused_state = metadata[:2]
  series = metadata[2]
  year = metadata[3:7]
  # 1-digit age is represented as ' 9' so trim the leading space.
  age = metadata[7:9].strip()

  if series == 'A':
    csvwriter = series_a_writer
  else:
    csvwriter = series_b_writer
  fields = data.split()
  processed_line = [year, age] + fields
  csvwriter.writerow(processed_line)

"""Group by year and aggregate regardless of age and gender.

Args:
  line: (str) a line of data read from input file (space seperated)
  projections: (dict) contains maps for A & B series projections
"""
def ParseAndMerge(line, projections):
  metadata = line[:9]
  data = line[9:]

  unused_state = metadata[:2]
  series = metadata[2]
  year = metadata[3:7]
  if year not in projections[series]:
    projections[series][year] = PopulationProjection()
  projection = projections[series][year]

  # Add up male and female figures and aggregate
  # population of any age as long as the projection is for the same year.
  fields = data.split()
  projection.white['non_hispanic'] += int(fields[0]) + int(fields[1])
  projection.white['hispanic'] += int(fields[2]) + int(fields[3])
  projection.black['non_hispanic'] += int(fields[4]) + int(fields[5])
  projection.black['hispanic'] += int(fields[6]) + int(fields[7])
  projection.indian_eskimo_aleut['non_hispanic'] += (
      int(fields[8]) + int(fields[9]))
  projection.indian_eskimo_aleut['hispanic'] += (
      int(fields[10]) + int(fields[11]))
  projection.asian_pacific['non_hispanic'] += int(fields[12]) + int(fields[13])
  projection.asian_pacific['hispanic'] += int(fields[14]) + int(fields[15])

def main():
  projections = {'A': {}, 'B': {}}
  parser = argparse.ArgumentParser(
      description='Parse population projection data from US Census Bureau.')
  parser.add_argument('-i', '--input', help='name of input data file')
  parser.add_argument(
      '--header', dest='header', action='store_true',
      help='print header in output CSV file')
  parser.add_argument('--no-header', dest='header', action='store_false',
      help='don\'t print header in output CSV file')
  parser.set_defaults(header=False)
  args = parser.parse_args()
  with open(args.input) as f:
    for line in f:
      ParseAndMerge(line, projections)
    for series in projections:
      filename = 'series_%s.csv' % series.lower()
      with open(filename, 'wb') as projection_file:
        csv_writer = csv.writer(projection_file)
        if args.header:
          csv_writer.writerow(['year',
              'White Non-Hispanic',
              'White Hispanic',
              'Black Non-Hispanic',
              'Black Hispanic',
              'American Indian, Eskimo, and Aleut Non-Hispanic',
              'American Indian, Eskimo, and Aleut Hispanic',
              'Asian and Pacific Islander Non-Hispanic',
              'Asian and Pacific Islander Hispanic',
              ])
        for year in sorted(projections[series]):
          projection = projections[series][year]
          print 'series %s year %s: %s' % (series, year, projection)
          csv_writer.writerow([year] + projection.GetAsList())


if __name__ == '__main__':
  main()
