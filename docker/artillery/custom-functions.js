'use strict';

module.exports = {
    generateRandomString,
    setupUser,
    logResponse
};

function generateRandomString(context, events, done) {
    const strings = [
        'laravel', 'performance', 'optimization', 'database', 'caching',
        'memory', 'query', 'response', 'scaling', 'benchmark'
    ];

    context.vars.randomString = strings[Math.floor(Math.random() * strings.length)];
    return done();
}

function setupUser(context, events, done) {
    context.vars.userId = Math.floor(Math.random() * 100) + 1;
    context.vars.sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);
    return done();
}

function logResponse(requestParams, response, context, events, done) {
    if (response.statusCode >= 400) {
        console.log(`Error ${response.statusCode} for ${requestParams.url}`);
    }

    if (response.timings && response.timings.response > 2000) {
        console.log(`Slow response (${response.timings.response}ms) for ${requestParams.url}`);
    }

    return done();
}
