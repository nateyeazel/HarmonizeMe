// import InlineWorker from 'inline-worker';

var Recorder = function(source, cfg) {
        var _this = this;


        this.config = {
            bufferLen: 4096,
            numChannels: 2,
            mimeType: 'audio/wav'
        };
        this.recording = false;
        this.callbacks = {
            getBuffer: [],
            exportWAV: []
        };

        Object.assign(this.config, cfg);
        this.context = source.context;
        this.node = (this.context.createScriptProcessor || this.context.createJavaScriptNode).call(this.context, this.config.bufferLen, this.config.numChannels, this.config.numChannels);

        this.node.onaudioprocess = function (e) {
            if (!_this.recording) return;

            var buffer = [];
            for (var channel = 0; channel < _this.config.numChannels; channel++) {
                buffer.push(e.inputBuffer.getChannelData(channel));
            }
            _this.worker.postMessage({
                command: 'record',
                buffer: buffer
            });
        };

        source.connect(this.node);
        this.node.connect(this.context.destination); //this should not be necessary

        var self = {};
        var recLength = 0,
            recBuffers = [],
            sampleRate = undefined,
            numChannels = undefined;

        self.onmessage = function (e) {
            switch (e.data.command) {
                case 'init':
                    init(e.data.config);
                    break;
                case 'record':
                    record(e.data.buffer);
                    break;
                case 'exportWAV':
                    exportWAV(e.data.type);
                    break;
                case 'getBuffer':
                    getBuffer();
                    break;
                case 'clear':
                    clear();
                    break;
            }
        };

        this.init = function(config) {
            sampleRate = config.sampleRate;
            numChannels = config.numChannels;
            initBuffers();
        };

        this.record = function(inputBuffer) {
            for (var channel = 0; channel < numChannels; channel++) {
                recBuffers[channel].push(inputBuffer[channel]);
            }
            recLength += inputBuffer[0].length;
        };

        this.exportWAV = function(type) {
            var buffers = [];
            for (var channel = 0; channel < numChannels; channel++) {
                buffers.push(mergeBuffers(recBuffers[channel], recLength));
            }
            var interleaved = undefined;
            if (numChannels === 2) {
                interleaved = interleave(buffers[0], buffers[1]);
            } else {
                interleaved = buffers[0];
            }
            var dataview = encodeWAV(interleaved);
            var audioBlob = new Blob([dataview], { type: type });

            this.postMessage({ command: 'exportWAV', data: audioBlob });
        };

        this.getBuffer = function() {
            var buffers = [];
            for (var channel = 0; channel < numChannels; channel++) {
                buffers.push(mergeBuffers(recBuffers[channel], recLength));
            }
            self.postMessage({ command: 'getBuffer', data: buffers });
        };

        this.clear = function() {
            recLength = 0;
            recBuffers = [];
            initBuffers();
        };

        this.initBuffers = function() {
            for (var channel = 0; channel < numChannels; channel++) {
                recBuffers[channel] = [];
            }
        };

        this.mergeBuffers = function(recBuffers, recLength) {
            var result = new Float32Array(recLength);
            var offset = 0;
            for (var i = 0; i < recBuffers.length; i++) {
                result.set(recBuffers[i], offset);
                offset += recBuffers[i].length;
            }
            return result;
        };

        this.interleave = function(inputL, inputR) {
            var length = inputL.length + inputR.length;
            var result = new Float32Array(length);

            var index = 0,
                inputIndex = 0;

            while (index < length) {
                result[index++] = inputL[inputIndex];
                result[index++] = inputR[inputIndex];
                inputIndex++;
            }
            return result;
        };

        this.floatTo16BitPCM = function(output, offset, input) {
            for (var i = 0; i < input.length; i++, offset += 2) {
                var s = Math.max(-1, Math.min(1, input[i]));
                output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
            }
        };

        this.writeString = function(view, offset, string) {
            for (var i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };

        this.encodeWAV = function(samples) {
            var buffer = new ArrayBuffer(44 + samples.length * 2);
            var view = new DataView(buffer);

            /* RIFF identifier */
            writeString(view, 0, 'RIFF');
            /* RIFF chunk length */
            view.setUint32(4, 36 + samples.length * 2, true);
            /* RIFF type */
            writeString(view, 8, 'WAVE');
            /* format chunk identifier */
            writeString(view, 12, 'fmt ');
            /* format chunk length */
            view.setUint32(16, 16, true);
            /* sample format (raw) */
            view.setUint16(20, 1, true);
            /* channel count */
            view.setUint16(22, numChannels, true);
            /* sample rate */
            view.setUint32(24, sampleRate, true);
            /* byte rate (sample rate * block align) */
            view.setUint32(28, sampleRate * 4, true);
            /* block align (channel count * bytes per sample) */
            view.setUint16(32, numChannels * 2, true);
            /* bits per sample */
            view.setUint16(34, 16, true);
            /* data chunk identifier */
            writeString(view, 36, 'data');
            /* data chunk length */
            view.setUint32(40, samples.length * 2, true);

            floatTo16BitPCM(view, 44, samples);

            return view;
        };
    };
