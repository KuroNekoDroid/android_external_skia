/* HELLO WORLD */

/**************************************************************************************************
 *** This file was autogenerated from GrDSLHelloWorld.fp; do not modify.
 **************************************************************************************************/
/* TODO(skia:11854): DSLCPPCodeGenerator is currently a work in progress. */
#include "GrDSLHelloWorld.h"

#include "src/core/SkUtils.h"
#include "src/gpu/GrTexture.h"
#include "src/gpu/glsl/GrGLSLFragmentProcessor.h"
#include "src/gpu/glsl/GrGLSLFragmentShaderBuilder.h"
#include "src/gpu/glsl/GrGLSLProgramBuilder.h"
#include "src/sksl/SkSLCPP.h"
#include "src/sksl/SkSLUtil.h"
class GrGLSLDSLHelloWorld : public GrGLSLFragmentProcessor {
public:
    GrGLSLDSLHelloWorld() {}
    void emitCode(EmitArgs& args) override {
        GrGLSLFPFragmentBuilder* fragBuilder = args.fFragBuilder;
        const GrDSLHelloWorld& _outer = args.fFp.cast<GrDSLHelloWorld>();
        (void) _outer;
        fragBuilder->codeAppendf(
R"SkSL(return half4(1.0);
)SkSL"
);
    }
private:
    void onSetData(const GrGLSLProgramDataManager& pdman, const GrFragmentProcessor& _proc) override {
    }
};
std::unique_ptr<GrGLSLFragmentProcessor> GrDSLHelloWorld::onMakeProgramImpl() const {
    return std::make_unique<GrGLSLDSLHelloWorld>();
}
void GrDSLHelloWorld::onGetGLSLProcessorKey(const GrShaderCaps& caps, GrProcessorKeyBuilder* b) const {
}
bool GrDSLHelloWorld::onIsEqual(const GrFragmentProcessor& other) const {
    const GrDSLHelloWorld& that = other.cast<GrDSLHelloWorld>();
    (void) that;
    return true;
}
GrDSLHelloWorld::GrDSLHelloWorld(const GrDSLHelloWorld& src)
: INHERITED(kGrDSLHelloWorld_ClassID, src.optimizationFlags()) {
        this->cloneAndRegisterAllChildProcessors(src);
}
std::unique_ptr<GrFragmentProcessor> GrDSLHelloWorld::clone() const {
    return std::make_unique<GrDSLHelloWorld>(*this);
}
#if GR_TEST_UTILS
SkString GrDSLHelloWorld::onDumpInfo() const {
    return SkString();
}
#endif
