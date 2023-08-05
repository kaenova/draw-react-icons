#! /usr/bin/env node

/**
 * This file is used to generate from svg to jpeg from react icons
 */

import fs from 'node:fs'
import path from 'node:path';
import sharp from 'sharp'
import assert from 'node:assert';
import yargs from 'yargs';

import { hideBin } from 'yargs/helpers'
import { fileURLToPath } from 'url';
import { renderToString } from 'react-dom/server';

import * as icons from 'react-icons'

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const argv = yargs(hideBin(process.argv))
  .option('size', {
    type: 'number',
    description: 'Rendered SVG Icon Size from react',
    default: 50
  })
  .option('out_dir', {
    type: 'string',
    description: "Output folder of generated image",
    default: 'dist'
  })
  .option('color', {
    type: 'string',
    description: "Color of the icons",
    default: 'black'
  })
  .option('pad_size', {
    type: 'number',
    description: 'Padding for image',
    default: 100
  })
  .parse()

const imageDir = path.resolve(__dirname, argv.out_dir)
const iconSize = argv.size
const iconColor = argv.color
const iconPadSize = argv.pad_size

async function dynamicReactIconsImport(iconParentID) {
  try {
    const module = await import(`react-icons/${iconParentID}/index.js`);
    return module.default
  } catch (error) {
    console.error('import failed', error);
  }
}

function printIconStats(iconFunction) {
  console.log("Icon Stats")

  const data = {}
  let iconTotal = 0
  const iconIDs = Object.keys(iconFunction)
  iconIDs.forEach(v => {
    let iconNums = Object.keys(iconFunction[v]).length
    data[v] = iconNums
    iconTotal += iconNums
  })
  data['total'] = iconTotal

  console.table(data)
}

async function renderJPGFromSVG(iconID, svgString, saveDirPath) {
  const savePath = path.resolve(saveDirPath, `${iconID}.jpg`)
  const background = { r: 255, g: 255, b: 255, alpha: 255 }
  await sharp(Buffer.from(svgString))
    // Make white Background
    .flatten({ background: background })
    // Pad the icon
    .extend({
      top: iconPadSize,
      right: iconPadSize,
      bottom: iconPadSize,
      left: iconPadSize,
      background: background
    })
    .jpeg({
      quality: 50,
      progressive: true,
      optimizeScans: true,
    })
    // .png({
    //   adaptiveFiltering: true,
    //   compressionLevel: 9,
    //   progressive: true,
    // })
    .toFile(savePath);
}

async function run() {
  if (fs.existsSync(imageDir)) {
    fs.rmSync(imageDir, { recursive: true })
  }

  // Get icon data id
  const iconsManifest = icons.IconsManifest
  assert(Array.isArray(iconsManifest))
  const iconParentIDs = iconsManifest.map(v => v.id)

  // Import Icons into dictionary
  const iconFunction = {
    // iconParentID : {IconID : SVGGen}
  }
  for (let i = 0; i < iconParentIDs.length; i++) {
    let id = iconParentIDs[i]
    let genFunction = await dynamicReactIconsImport(id)
    iconFunction[id] = genFunction
  }

  // Printing current icons number
  printIconStats(iconFunction)

  // Icon generate svg
  const iconSVG = {
    // iconParentID : {IconID : SVG String}
  }
  for (let i = 0; i < iconParentIDs.length; i++) {
    const parentID = iconParentIDs[i]
    const data = {
      // IconID : SVG String
    }
    const iconParent = iconFunction[parentID]
    const iconID = Object.keys(iconParent)
    console.log(`Rendering SVG for IconParentID: ${parentID}`)
    iconID.forEach(v => {
      let reactElm = iconParent[v]({
        size: iconSize,
        color: iconColor
      }) // iconParent[v] is a function to render react element
      data[v] = renderToString(reactElm)
    })
    iconSVG[parentID] = data
  }

  // Generate Image from 
  if (!fs.existsSync(imageDir)) {
    fs.mkdirSync(imageDir)
  }
  const promises = []
  for (let i = 0; i < iconParentIDs.length; i++) {

    const parentID = iconParentIDs[i]
    const iconParent = iconSVG[parentID]
    const iconID = Object.keys(iconParent)

    let iconSavePath = path.resolve(imageDir, parentID)
    if (!fs.existsSync(iconSavePath)) {
      fs.mkdirSync(iconSavePath)
    }

    console.log(`Rendering JPG Icon of IconParentID ${parentID} to ${iconSavePath}`)
    iconID.forEach(v => {
      let svgString = iconParent[v]
      promises.push(renderJPGFromSVG(v, svgString, iconSavePath))

    })
  }
  console.log("Waiting renders to be done...")
  await Promise.all(promises)
  console.log("Process Complete")
}

run()