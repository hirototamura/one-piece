package CubeHoldMigration {
    requirement hold {
        doc /* After manual placement and release, the Cube shall hold its vertex position for at least 30 s without external support. */
    }
    part controller;
    action balanceControl;
    attribute cubeSide = 0.18[SI::m];
    dependency holdToBalance from hold to balanceControl;
    dependency balanceToController from balanceControl to controller;
}
