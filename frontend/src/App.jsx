import React, { useRef, useState, useEffect } from 'react';
import { Stage, Layer, Image as KonvaImage } from 'react-konva';
import axios from 'axios';

export default function App() {
  const [bgImage, setBgImage] = useState(null);
  const [probMaskImage, setProbMaskImage] = useState(null);
  const [editedMaskImage, setEditedMaskImage] = useState(null);
  const [imageSize, setImageSize] = useState({ width: 800, height: 600 });
  const [threshold, setThreshold] = useState(0.6);
  const [brushSize, setBrushSize] = useState(6);
  const [tool, setTool] = useState('pointer');
  const [isDrawing, setIsDrawing] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [history, setHistory] = useState([]);

  const stageRef = useRef();
  const canvasRef = useRef(null);
  const updateTimeout = useRef(null);
  const lastPointerPos = useRef(null);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault();
        undoLastAction();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [history]);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async () => {
      const img = new window.Image();
      img.src = reader.result;
      img.onload = () => {
        setBgImage(img);
        setImageSize({ width: img.width, height: img.height });
      };

      const formData = new FormData();
      formData.append('file', file);
      const res = await axios.post('http://localhost:8000/predict/', formData, {
        responseType: 'blob',
      });

      const blobURL = URL.createObjectURL(res.data);
      const probImg = new window.Image();
      probImg.src = blobURL;
      probImg.onload = () => {
        setProbMaskImage(probImg);
      };
    };
    reader.readAsDataURL(file);
  };

  useEffect(() => {
    if (!probMaskImage) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    canvas.width = probMaskImage.width;
    canvas.height = probMaskImage.height;

    ctx.drawImage(probMaskImage, 0, 0);
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    for (let i = 0; i < data.length; i += 4) {
      const val = data[i];
      if (val / 255 >= threshold) {
        data[i] = 255; data[i + 1] = 255; data[i + 2] = 0; data[i + 3] = 255;
      } else {
        data[i] = 128; data[i + 1] = 0; data[i + 2] = 128; data[i + 3] = 255;
      }
    }

    ctx.putImageData(imageData, 0, 0);
    const img = new window.Image();
    const url = canvas.toDataURL();
    img.src = url;
    img.onload = () => {
      setEditedMaskImage(img);
      setHistory([url]);
    };
  }, [probMaskImage, threshold]);

  const drawAt = (x, y) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.beginPath();
    ctx.arc(x, y, brushSize / 2, 0, 2 * Math.PI);
    ctx.fillStyle = tool === 'eraser' ? 'rgb(128,0,128)' : 'rgb(255,255,0)';
    ctx.fill();

    if (updateTimeout.current) clearTimeout(updateTimeout.current);
    updateTimeout.current = setTimeout(() => {
      const newImg = new Image();
      const url = canvas.toDataURL();
      newImg.src = url;
      newImg.onload = () => {
        setEditedMaskImage(newImg);
        setHistory(prev => {
          const newHist = [...prev, url];
          return newHist.length > 3 ? newHist.slice(newHist.length - 3) : newHist;
        });
      };
    }, 1000);
  };

  const handleMouseDown = () => {
    if (tool === 'brush' || tool === 'eraser') {
      setIsDrawing(true);
      const stage = stageRef.current;
      const pointer = stage.getPointerPosition();
      const transform = stage.getAbsoluteTransform().copy().invert();
      const local = transform.point(pointer);
      drawAt(local.x, local.y);
      lastPointerPos.current = local;
    }
  };

  const handleMouseMove = () => {
    if (!isDrawing) return;
    const stage = stageRef.current;
    const pointer = stage.getPointerPosition();
    const transform = stage.getAbsoluteTransform().copy().invert();
    const local = transform.point(pointer);

    if (!lastPointerPos.current) {
      drawAt(local.x, local.y);
      lastPointerPos.current = local;
      return;
    }

    const dx = local.x - lastPointerPos.current.x;
    const dy = local.y - lastPointerPos.current.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const steps = Math.ceil(dist / (brushSize / 2));

    for (let i = 0; i <= steps; i++) {
      const x = lastPointerPos.current.x + (dx * i) / steps;
      const y = lastPointerPos.current.y + (dy * i) / steps;
      drawAt(x, y);
    }

    lastPointerPos.current = local;
  };

  const handleMouseUp = () => {
    setIsDrawing(false);
    lastPointerPos.current = null;
  };

  const handleWheel = (e) => {
    e.evt.preventDefault();
    const scaleBy = 1.05;
    const stage = stageRef.current;
    const oldScale = stage.scaleX();
    const pointer = stage.getPointerPosition();
    const mousePointTo = {
      x: (pointer.x - stage.x()) / oldScale,
      y: (pointer.y - stage.y()) / oldScale
    };
    const newScale = e.evt.deltaY > 0 ? oldScale / scaleBy : oldScale * scaleBy;
    stage.scale({ x: newScale, y: newScale });
    setZoom(newScale);
    const newPos = {
      x: pointer.x - mousePointTo.x * newScale,
      y: pointer.y - mousePointTo.y * newScale
    };
    stage.position(newPos);
    stage.batchDraw();
  };

  const undoLastAction = () => {
    if (history.length <= 1) return;
    const newHistory = [...history.slice(0, -1)];
    const lastURL = newHistory[newHistory.length - 1];
    const img = new window.Image();
    img.src = lastURL;
    img.onload = () => {
      setEditedMaskImage(img);
      setHistory(newHistory);
      const ctx = canvasRef.current.getContext('2d');
      const image = new window.Image();
      image.src = lastURL;
      image.onload = () => ctx.drawImage(image, 0, 0);
    };
  };

  const resetMask = () => {
    if (history.length === 0) return;
    const original = history[0];
    const img = new window.Image();
    img.src = original;
    img.onload = () => {
      setEditedMaskImage(img);
      setHistory([original]);
      const ctx = canvasRef.current.getContext('2d');
      ctx.drawImage(img, 0, 0);
    };
  };

  const downloadMask = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i], g = data[i + 1], b = data[i + 2];
      if (r === 255 && g === 255 && b === 0) {
        data[i] = data[i + 1] = data[i + 2] = 255;
      } else {
        data[i] = data[i + 1] = data[i + 2] = 0;
      }
    }

    ctx.putImageData(imageData, 0, 0);
    const link = document.createElement('a');
    link.download = 'edited_mask.png';
    link.href = canvas.toDataURL();
    link.click();
  };

  return (
    <div>
      <h2>Cuneiform Detector</h2>
      <input type="file" accept="image/*" onChange={handleUpload} />

      <div style={{ marginTop: 10 }}>
        <label>Threshold: {threshold.toFixed(2)}
          <input type="range" min="0.3" max="0.9" step="0.01"
                 value={threshold} onChange={e => setThreshold(+e.target.value)}
                 style={{ width: 200, marginLeft: 10 }} />
        </label>

        <label style={{ marginLeft: 20 }}>Tool:
          <select value={tool} onChange={e => setTool(e.target.value)} style={{ marginLeft: 10 }}>
            <option value="pointer">Hand Tool</option>
            <option value="brush">Brush</option>
            <option value="eraser">Eraser</option>
          </select>
        </label>

        <label style={{ marginLeft: 20 }}>Brush Size: {brushSize}
          <input type="range" min="2" max="30" step="1"
                 value={brushSize} onChange={e => setBrushSize(+e.target.value)}
                 disabled={tool === 'pointer'} style={{ marginLeft: 10 }} />
        </label>

        <button onClick={undoLastAction} style={{ marginLeft: 20 }}>Undo last action</button>
        <button onClick={resetMask} style={{ marginLeft: 10 }}>Reset Mask</button>
        <button onClick={downloadMask} style={{ marginLeft: 10 }}>Download</button>
      </div>

      <div
        style={{ border: '1px solid #ccc', marginTop: 10, overflow: 'hidden' }}
        onWheel={(e) => e.preventDefault()}
      >
        <Stage ref={stageRef} width={imageSize.width} height={imageSize.height}
               draggable={tool === 'pointer'}
               onMouseDown={handleMouseDown} onMouseMove={handleMouseMove} onMouseUp={handleMouseUp}
               onWheel={handleWheel}>
          <Layer>
            {bgImage && <KonvaImage image={bgImage} />}
            {editedMaskImage && <KonvaImage image={editedMaskImage} opacity={0.5} />}
          </Layer>
        </Stage>
      </div>

      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  );
}
