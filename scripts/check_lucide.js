import * as lucide from 'lucide-react';

const iconsToCheck = [
  'AlertTriangle',
  'TriangleAlert',
  'BarChart3',
  'BarChart',
  'CheckCircle2',
  'CheckCircle',
  'Sun',
  'Moon',
];

iconsToCheck.forEach((icon) => {
  console.log(`${icon}: ${lucide[icon] ? 'EXISTS' : 'MISSING'}`);
});
