'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
test('Distribution propre et reproductible : uniquement actifs exécutables, aucun profil, export ou dépendance', () => {
  const root = path.resolve(__dirname, '../../..');
  const first = JSON.parse(execFileSync('python', ['tools/package_collector.py'], { cwd: root, encoding: 'utf8' }));
  const zip = fs.readFileSync(first.archive);
  const second = JSON.parse(execFileSync('python', ['tools/package_collector.py'], { cwd: root, encoding: 'utf8' }));
  assert.deepEqual(fs.readFileSync(second.archive), zip);
  const files = fs.readdirSync(first.folder, { recursive: true, withFileTypes: true }).filter(e => e.isFile());
  assert.equal(files.length, first.files); assert.equal(first.files, 16); assert.ok(first.zipBytes < 100000);
  assert.ok(files.every(f => !/node_modules|\.recette|tests|package-lock|exports|README/.test(path.join(f.parentPath, f.name).slice(first.folder.length))));
  assert.equal(JSON.parse(fs.readFileSync(path.join(first.folder, 'manifest.json'))).version, '0.8.1');
});
