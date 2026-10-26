const coursePlan = require('./src/_data/beginnerCourse.json');

module.exports = function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ 'src/assets': 'assets' });
  // Keep adjacent table cells separate in Pagefind's plain-text excerpts.
  eleventyConfig.addTransform('table-search-spacing', function(content) {
    if (this.page.outputPath?.endsWith('.html')) {
      return content.replace(/(?<!\s)<\/(td|th)>/gi, ' </$1>');
    }
    return content;
  });
  eleventyConfig.addCollection('lessons', api => api.getFilteredByTag('lesson').sort((a,b) => a.data.title.localeCompare(b.data.title, 'en')));
  eleventyConfig.addCollection('beginnerCourse', api => {
    const lessons = api.getFilteredByTag('lesson');
    return coursePlan.map((step, index) => ({ ...step, position: index + 1, lesson: lessons.find(lesson => lesson.url === step.url) }));
  });
  eleventyConfig.addCollection('featuredLessons', api => api.getFilteredByTag('lesson').filter(lesson => lesson.data.featured).sort((a,b) => a.data.featured - b.data.featured).slice(0, 3));
  eleventyConfig.addFilter('courseEntry', (url, course) => course.find(step => step.url === url));
  eleventyConfig.addFilter('coursePrevious', (url, course) => course[course.findIndex(step => step.url === url) - 1]);
  eleventyConfig.addFilter('courseNext', (url, course) => {
    const index = course.findIndex(step => step.url === url);
    return index >= 0 ? course[index + 1] : undefined;
  });
  eleventyConfig.addFilter('selectedLessons', (urls, lessons) => (urls || []).map(url => lessons.find(lesson => lesson.url === url)).filter(Boolean).slice(0, 2));
  eleventyConfig.addFilter('urlpath', path => (process.env.SITE_PATH_PREFIX || '').replace(/\/$/, '') + path);
  return { dir: { input: 'src', output: '_site', includes: '_includes' }, markdownTemplateEngine: 'njk' };
};
